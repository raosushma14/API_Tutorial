from pydantic import BaseModel, EmailStr, Field

class Person(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name:  str = Field(..., min_length=1, max_length=100)
    email:      EmailStr
    age:        int | None = None
