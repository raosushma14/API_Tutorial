from sqlalchemy import Column, Integer, String, Date
from app.db import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    title = Column(String(150), nullable=True)
    start_date = Column(Date, nullable=True)
