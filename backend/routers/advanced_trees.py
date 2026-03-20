from fastapi import APIRouter, HTTPException
from services.advanced_trees_service import (
    delete_tree_value,
    get_tree_state,
    insert_tree_value,
    reset_tree,
    search_tree_value,
    traverse_tree,
)

router = APIRouter(prefix="/api/advanced", tags=["advanced-trees"])


@router.get("/{tree_type}/state/{db_id}")
def get_tree_state_route(tree_type: str, db_id: int) -> dict:
    try:
        return {"success": True, "data": get_tree_state(tree_type, db_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{tree_type}/insert/{db_id}")
def insert_tree_value_route(tree_type: str, db_id: int, value: int) -> dict:
    try:
        return {
            "success": True,
            "message": f"Inserted {value} into {tree_type}",
            "data": insert_tree_value(tree_type, db_id, value),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{tree_type}/delete/{db_id}")
def delete_tree_value_route(tree_type: str, db_id: int, value: int) -> dict:
    try:
        return {
            "success": True,
            "message": f"Deleted {value} from {tree_type}",
            "data": delete_tree_value(tree_type, db_id, value),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{tree_type}/search/{db_id}")
def search_tree_value_route(tree_type: str, db_id: int, value: int) -> dict:
    try:
        path, found = search_tree_value(tree_type, db_id, value)
        return {
            "success": True,
            "treeType": tree_type,
            "target": value,
            "found": found,
            "steps": path,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{tree_type}/traverse/{db_id}/{method}")
def traverse_tree_route(tree_type: str, db_id: int, method: str) -> dict:
    try:
        steps = traverse_tree(tree_type, db_id, method)
        return {"success": True, "treeType": tree_type, "method": method, "steps": steps}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{tree_type}/reset/{db_id}")
def reset_tree_route(tree_type: str, db_id: int) -> dict:
    try:
        return {"success": True, "message": f"Reset {tree_type}", "data": reset_tree(tree_type, db_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
