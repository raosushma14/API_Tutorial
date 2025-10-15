import os
os.environ["DB_NAME"] = "employee_db"  # ensure test DB if you have one
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_list_delete_employee():
    payload = {"first_name":"Ava","last_name":"Singh","email":"ava@example.com","age":30,"salary":90000}
    r = client.post("/employees", json=payload)
    assert r.status_code == 201
    emp = r.json()
    emp_id = emp["id"]                 

    r = client.get("/employees")
    assert r.status_code == 200
    assert any(e["id"] == emp_id for e in r.json())

    r = client.delete(f"/employees/{emp_id}")
    assert r.status_code == 204

