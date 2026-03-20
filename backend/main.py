"""FastAPI backend for Visual Algorithm Simulator."""

from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Make project packages importable when running backend/main.py directly.
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.routers import advanced_trees, bst, hash_table, health, recursion, system, tree

app = FastAPI(title="Algorithm Simulator API", version="1.0.0")

# CORS configuration for React frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(bst.router)
app.include_router(hash_table.router)
app.include_router(tree.router)
app.include_router(recursion.router)
app.include_router(system.router)
app.include_router(advanced_trees.router)

# In container/production mode we serve the built frontend from FastAPI.
frontend_dist = project_root / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
