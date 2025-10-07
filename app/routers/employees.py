from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/employees", tags=["Employees"])

# CREATE
@router.post("/", response_model=schemas.EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Unique email check
    exists = db.scalar(select(models.Employee).where(models.Employee.email == payload.email))
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")

    emp = models.Employee(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        title=payload.title,
        start_date=payload.start_date,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

# READ (list)
@router.get("/", response_model=List[schemas.EmployeeRead])
def list_employees(db: Session = Depends(get_db), limit: int = 50, offset: int = 0, search: str | None = None):
    stmt = select(models.Employee)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            (models.Employee.first_name.ilike(like)) |
            (models.Employee.last_name.ilike(like)) |
            (models.Employee.email.ilike(like)) |
            (models.Employee.title.ilike(like))
        )
    stmt = stmt.offset(offset).limit(limit)
    return list(db.scalars(stmt))

# READ (single)
@router.get("/{employee_id}", response_model=schemas.EmployeeRead)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

# UPDATE (PUT = replace or PATCH = partial; we’ll implement PATCH-style)
@router.patch("/{employee_id}", response_model=schemas.EmployeeRead)
def update_employee(employee_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if payload.email and payload.email != emp.email:
        exists = db.scalar(select(models.Employee).where(models.Employee.email == payload.email))
        if exists:
            raise HTTPException(status_code=400, detail="Email already exists")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)

    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

# UPDATE (PUT variant: require all fields)
@router.put("/{employee_id}", response_model=schemas.EmployeeRead)
def replace_employee(employee_id: int, payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Email conflict check if changed
    if payload.email != emp.email:
        exists = db.scalar(select(models.Employee).where(models.Employee.email == payload.email))
        if exists:
            raise HTTPException(status_code=400, detail="Email already exists")

    emp.first_name = payload.first_name
    emp.last_name = payload.last_name
    emp.email = payload.email
    emp.title = payload.title
    emp.start_date = payload.start_date

    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

# DELETE
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    return
