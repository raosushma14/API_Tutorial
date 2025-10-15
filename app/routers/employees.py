from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.models.employee import EmployeeCreate, EmployeeRead
from app.db import db_utils

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(payload: EmployeeCreate):
    try:
        row = db_utils.add_employee(
            payload.first_name, payload.last_name,
            payload.email, payload.age, payload.salary
        )
        return EmployeeRead(**row)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[EmployeeRead])
def list_employees():
    rows = db_utils.get_all_employees()
    return [EmployeeRead(**r) for r in rows]

@router.delete("/{emp_id}", status_code=204)
def delete_employee(emp_id: UUID):
    ok = db_utils.delete_employee_by_id(emp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    return
