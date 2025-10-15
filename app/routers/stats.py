# app/routers/stats.py
from fastapi import APIRouter
from app.db import db_utils

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/median-age")
def median_age():
    return {"median_age": db_utils.get_median_age()}

@router.get("/median-salary")
def median_salary():
    return {"median_salary": db_utils.get_median_salary()}
