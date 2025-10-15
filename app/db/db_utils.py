import os
import psycopg
from psycopg.rows import dict_row
from uuid import UUID
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    url = os.getenv("DATABASE_URL")
    if url:
        url = url.replace("postgresql+psycopg://", "postgresql://")
        return psycopg.connect(url)
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def add_employee(first_name, last_name, email, age, salary):
    sql = """
    INSERT INTO employees (first_name, last_name, email, age, salary)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, first_name, last_name, email, age, salary;
    """
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, (first_name, last_name, email, age, salary))
        return cur.fetchone()

def get_all_employees():
    sql = "SELECT id, first_name, last_name, email, age, salary FROM employees ORDER BY id;"
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        return cur.fetchall()

def delete_employee_by_id(emp_id: UUID) -> bool:
    sql = "DELETE FROM employees WHERE id = %s;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (emp_id,))  
        return cur.rowcount > 0

def get_median_age():
    sql = "SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY age) FROM employees WHERE age IS NOT NULL;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
        return row[0] if row else None

def get_median_salary():
    sql = "SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY salary) FROM employees WHERE salary IS NOT NULL;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
        return float(row[0]) if row and row[0] is not None else None
