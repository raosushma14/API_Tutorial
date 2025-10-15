import os
import uuid
import types
import pytest

from app.db import db_utils

class FakeCursor:
    
    def __init__(self):
        self._last_sql = ""
        self._last_params = None
        self._fetch_queue = []
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False  # don't suppress

    def execute(self, sql, params=None):
        self._last_sql = " ".join(sql.split()).lower()
        self._last_params = params
        self._fetch_queue.clear()
        self.rowcount = 0

        # Route based on SQL content
        if self._last_sql.startswith("insert into employees"):
            # Simulate a successful insert returning a record dict
            new_id = uuid.uuid4()
            self._fetch_queue.append({
                "id": new_id,
                "first_name": params[0],
                "last_name":  params[1],
                "email":      params[2],
                "age":        params[3],
                "salary":     params[4],
            })
            self.rowcount = 1

        elif self._last_sql.startswith("select id, first_name"):
            # Simulate listing employees (two rows)
            self._fetch_queue.extend([
                {
                    "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                    "first_name": "test",
                    "last_name":  "test",
                    "email":      "test@example.com",
                    "age":        30,
                    "salary":     90000.0,
                },
                {
                    "id": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                    "first_name": "xyz",
                    "last_name":  "abc",
                    "email":      "xyz@example.com",
                    "age":        28,
                    "salary":     80000.0,
                },
            ])

        elif "delete from employees" in self._last_sql:
            # Simulate delete: we can toggle via a param flag in tests
            # Default to success:
            self.rowcount = 1

        elif "percentile_cont(0.5) within group (order by age)" in self._last_sql:
            # Return a single-row, single-column tuple for median age
            self._fetch_queue.append((29.0,))

        elif "percentile_cont(0.5) within group (order by salary)" in self._last_sql:
            # Return a single-row, single-column tuple for median salary
            self._fetch_queue.append((85000.00,))

        else:
            # Unexpected SQL in unit tests
            raise AssertionError(f"Unhandled SQL in FakeCursor: {self._last_sql}")

    def fetchone(self):
        return self._fetch_queue.pop(0) if self._fetch_queue else None

    def fetchall(self):
        out = list(self._fetch_queue)
        self._fetch_queue.clear()
        return out


class FakeConn:
    def __init__(self, cursor_obj: FakeCursor | None = None):
        self._cursor = cursor_obj or FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False  

    
    def cursor(self, *args, **kwargs):
       
        return self._cursor



@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
   
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://emp_user:emp_pass@127.0.0.1:5432/employee_db"
    )
    yield


@pytest.fixture
def connect_ok(monkeypatch):
    
    fake = FakeConn()
    # Build a dummy psycopg module shim to satisfy import in db_utils
    fake_psycopg = types.SimpleNamespace(connect=lambda *a, **k: fake)
    # Patch where db_utils imports it
    monkeypatch.setattr(db_utils, "psycopg", fake_psycopg, raising=True)
    return fake


# ---------- Tests for each function ----------

def test_add_employee_returns_row_dict(connect_ok):
    row = db_utils.add_employee(
        first_name="sushma",
        last_name="rao",
        email="user@example.com",
        age=30,
        salary=100000.00,
    )
    assert isinstance(row, dict)
    assert row["first_name"] == "sushma"
    assert row["email"] == "user@example.com"
    # UUID instance is fine, but JSON later will stringify in FastAPI
    assert isinstance(row["id"], uuid.UUID)


def test_get_all_employees_returns_list_of_dicts(connect_ok):
    rows = db_utils.get_all_employees()
    assert isinstance(rows, list)
    assert len(rows) == 2
    assert rows[0]["email"] == "test@example.com"
    assert rows[1]["salary"] == 80000.0


def test_delete_employee_by_id_success_true(connect_ok):
    emp_id = uuid.uuid4()
    ok = db_utils.delete_employee_by_id(emp_id)
    assert ok is True


def test_delete_employee_by_id_not_found_false(monkeypatch):
    # Make a FakeCursor that sets rowcount = 0 for DELETE
    class CursorNoDelete(FakeCursor):
        def execute(self, sql, params=None):
            super().execute(sql, params)
            if "delete from employees" in self._last_sql:
                self.rowcount = 0  # simulate not found

    fake = FakeConn(CursorNoDelete())
    fake_psycopg = types.SimpleNamespace(connect=lambda *a, **k: fake)
    monkeypatch.setattr(db_utils, "psycopg", fake_psycopg, raising=True)

    emp_id = uuid.uuid4()
    ok = db_utils.delete_employee_by_id(emp_id)
    assert ok is False


def test_get_median_age_returns_number(connect_ok):
    median = db_utils.get_median_age()
    assert isinstance(median, (int, float))
    assert median == 29.0


def test_get_median_salary_returns_float(connect_ok):
    median = db_utils.get_median_salary()
    assert isinstance(median, float)
    assert median == 85000.00


def test_get_median_age_none_when_no_rows(monkeypatch):
    class CursorNoAge(FakeCursor):
        def execute(self, sql, params=None):
            # Run base logic but then clear result for age query
            super().execute(sql, params)
            if "percentile_cont(0.5) within group (order by age)" in self._last_sql:
                self._fetch_queue.clear()  # simulate no rows

    fake = FakeConn(CursorNoAge())
    fake_psycopg = types.SimpleNamespace(connect=lambda *a, **k: fake)
    monkeypatch.setattr(db_utils, "psycopg", fake_psycopg, raising=True)

    assert db_utils.get_median_age() is None


def test_get_median_salary_none_when_no_rows(monkeypatch):
    class CursorNoSalary(FakeCursor):
        def execute(self, sql, params=None):
            super().execute(sql, params)
            if "percentile_cont(0.5) within group (order by salary)" in self._last_sql:
                self._fetch_queue.clear()

    fake = FakeConn(CursorNoSalary())
    fake_psycopg = types.SimpleNamespace(connect=lambda *a, **k: fake)
    monkeypatch.setattr(db_utils, "psycopg", fake_psycopg, raising=True)

    assert db_utils.get_median_salary() is None
