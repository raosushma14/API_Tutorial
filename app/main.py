from fastapi import FastAPI
from app.config import settings
from app.db import Base, engine
from app.routers import employees

app = FastAPI(title=settings.app_name, debug=settings.app_debug)

# Auto-create tables on startup (simple for learning; for teams use Alembic)
Base.metadata.create_all(bind=engine)

# Health/root
@app.get("/")
def root():
    return {"status": "ok", "service": settings.app_name}

# Routers
app.include_router(employees.router)
