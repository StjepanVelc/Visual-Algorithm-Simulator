from fastapi import APIRouter, HTTPException

from services.adt_service import add_recursion_call

from .shared import DB_PATH, full_state

router = APIRouter(prefix="/api/recursion", tags=["recursion"])


@router.get("/state/{db_id}")
def get_recursion_state(db_id: int) -> dict:
    del db_id
    try:
        state = full_state()
        return {"success": True, "data": state["recursion_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/insert/{db_id}")
def insert_recursion_node(db_id: int, parent_id: int | None = None, value: int | None = None) -> dict:
    del db_id
    try:
        parent = None if parent_id is None or parent_id < 0 else parent_id
        argument = str(value if value is not None else "0")
        add_recursion_call(DB_PATH, f"f({argument})", "f", argument, None, parent)
        state = full_state()
        return {"success": True, "message": "Inserted node", "data": state["recursion_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
