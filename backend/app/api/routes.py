from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/")
async def read_root():
    return {"message": "vk-lip backend is running"}

@router.get("/health")
async def api_health():
    return {"status": "ok"}
