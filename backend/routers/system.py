from fastapi import APIRouter, HTTPException

from services.adt_service import build_database

from .shared import DB_PATH

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/list-databases")
def list_databases() -> dict:
    try:
        return {"success": True, "databases": [{"id": 1, "name": DB_PATH.name, "path": str(DB_PATH)}]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/create-database/{adt_type}")
def create_database(adt_type: str, db_name: str = "default") -> dict:
    try:
        del adt_type
        del db_name
        build_database(DB_PATH)
        return {"success": True, "db_id": 1, "message": "Database reinitialized"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/clear-database/{db_id}")
def clear_database(db_id: int) -> dict:
    del db_id
    try:
        build_database(DB_PATH)
        return {"success": True, "message": "Database cleared"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
