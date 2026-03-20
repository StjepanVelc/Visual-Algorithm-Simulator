from fastapi import APIRouter, HTTPException

from services.traversal_service import build_general_traversal_order
from services.adt_service import add_general_tree_node

from .shared import DB_PATH, full_state

router = APIRouter(prefix="/api/tree", tags=["tree"])


@router.get("/state/{db_id}")
def get_tree_state(db_id: int) -> dict:
    del db_id
    try:
        state = full_state()
        return {"success": True, "data": state["opce_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/insert/{db_id}/{parent_id}")
def insert_tree_node(db_id: int, parent_id: int, value: int) -> dict:
    del db_id
    try:
        parent = None if parent_id < 0 else parent_id
        add_general_tree_node(DB_PATH, str(value), parent, None)
        state = full_state()
        return {"success": True, "message": f"Inserted {value}", "data": state["opce_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/traverse/{db_id}/{method}")
def traverse_tree(db_id: int, method: str) -> dict:
    del db_id
    try:
        state = full_state()
        mode = "DFS" if method.lower() == "dfs" else "BFS"
        steps = build_general_traversal_order(state["opce_rows"], mode)
        return {"success": True, "method": method, "steps": steps}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
