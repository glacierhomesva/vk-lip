import os

from fastapi import FastAPI

from sqlalchemy import text
from app.db.database import SessionLocal

app = FastAPI(
    title="VK Land Intelligence Platform",
    version="0.1.0",
    description="Acquisition Intelligence Platform for Residential Developers"
)


@app.get("/")
def root():
    return {
        "application": "VK-LIP",
        "message": "Welcome to VK Land Intelligence Platform",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "not connected",
        "version": "0.1.0"
    }

@app.get("/db-test")
def db_test():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version();"))
        version = result.scalar()
        db.close()

        return {
            "status": "connected",
            "database": version
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    
    import os

@app.get("/config")
def config():
    url = os.getenv("DATABASE_URL", "")
    if "@" in url:
        left, right = url.split("@", 1)
        # Hide the password but keep the rest visible
        user_part = left.split(":", 1)[0]
        return {"database_url": f"{user_part}:********@{right}"}
    return {"database_url": url}