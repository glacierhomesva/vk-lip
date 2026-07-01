from fastapi import FastAPI

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