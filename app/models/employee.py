from uuid import UUID
from pydantic import BaseModel, Field
from .person import Person

class Employee(Person):
    salary: float | None = Field(default=None, ge=0)

class EmployeeCreate(Employee):
    pass

class EmployeeRead(Employee):
    id: UUID      
    class Config:
        from_attributes = True
