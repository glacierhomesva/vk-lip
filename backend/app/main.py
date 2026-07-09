import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from app.db.database import SessionLocal

app = FastAPI(
    title="VK Land Intelligence Platform",
    version="0.1.0",
    description="Acquisition Intelligence Platform for Residential Developers"
)


def _cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "")
    parsed = [origin.strip() for origin in configured.split(",") if origin.strip()]
    if parsed:
        return parsed
    return ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.parcels import router as parcel_router
from app.api.opportunities import router as opportunity_router

app.include_router(parcel_router)
app.include_router(opportunity_router)


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