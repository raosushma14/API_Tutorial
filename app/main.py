# app/main.py
from fastapi import FastAPI
from app.routers import employees, stats

app = FastAPI(title="Employee Management API")

# health/root
@app.get("/")
def root():
    return {"status": "ok"}

# mount routers
app.include_router(employees.router)
app.include_router(stats.router)
