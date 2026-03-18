from fastapi import APIRouter

from .shared import DB_PATH

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "db_path": str(DB_PATH)}
