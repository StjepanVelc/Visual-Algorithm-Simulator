from fastapi import APIRouter, HTTPException

from services.adt_service import add_hash_node, delete_hash_node

from .shared import DB_PATH, full_state

router = APIRouter(prefix="/api/hash", tags=["hash"])


@router.get("/state/{db_id}")
def get_hash_state(db_id: int) -> dict:
    del db_id
    try:
        state = full_state()
        return {"success": True, "data": state["hash_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/insert/{db_id}")
def insert_hash_item(db_id: int, key: str, value: str) -> dict:
    del db_id
    try:
        bucket = sum(ord(ch) for ch in key) % 8
        add_hash_node(DB_PATH, bucket, key, value)
        state = full_state()
        return {"success": True, "message": f"Inserted {key}", "data": state["hash_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/delete/{db_id}")
def delete_hash_item(db_id: int, key: str) -> dict:
    del db_id
    try:
        rows = full_state()["hash_rows"]
        row = next((item for item in rows if item.get("kljuc") == key), None)
        if row is None:
            raise ValueError(f"Hash key not found: {key}")
        delete_hash_node(DB_PATH, int(row["cvor_id"]))
        state = full_state()
        return {"success": True, "message": f"Deleted {key}", "data": state["hash_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
