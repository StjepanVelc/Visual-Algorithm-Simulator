from fastapi import APIRouter, HTTPException

from presentation.canvas.traversals import build_bst_traversal_order
from services.adt_service import delete_bst_node as delete_bst_leaf
from services.adt_service import insert_bst_node_auto

from .shared import DB_PATH, full_state

router = APIRouter(prefix="/api/bst", tags=["bst"])


@router.get("/state/{db_id}")
def get_bst_state(db_id: int) -> dict:
    del db_id
    try:
        state = full_state()
        return {"success": True, "data": state["bst_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/insert/{db_id}")
def insert_bst_node(db_id: int, value: int) -> dict:
    del db_id
    try:
        result = insert_bst_node_auto(DB_PATH, str(value))
        state = full_state()
        return {
            "success": True,
            "message": f"Inserted {value}",
            "insert": result,
            "data": state["bst_rows"],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/delete/{db_id}")
def delete_bst_node(db_id: int, value: int) -> dict:
    del db_id
    try:
        delete_bst_leaf(DB_PATH, value)
        state = full_state()
        return {"success": True, "message": f"Deleted {value}", "data": state["bst_rows"]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/traverse/{db_id}/{method}")
def traverse_bst(db_id: int, method: str) -> dict:
    del db_id
    try:
        state = full_state()
        mode = {"bfs": "BFS", "dfs": "DFS", "search": "BST Search"}.get(method.lower(), "BFS")
        steps = build_bst_traversal_order(state["bst_rows"], mode)
        return {"success": True, "method": method, "steps": steps}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
