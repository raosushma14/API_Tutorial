from datetime import date
from pydantic import BaseModel, EmailStr, Field

# What we send/receive over the API

class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    title: str | None = Field(default=None, max_length=150)
    start_date: date | None = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    # All fields optional for PATCH; also works for PUT if you want partials
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    title: str | None = Field(default=None, max_length=150)
    start_date: date | None = None

class EmployeeRead(EmployeeBase):
    id: int

    class Config:
        from_attributes = True
