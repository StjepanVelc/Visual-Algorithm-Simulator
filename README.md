# Visual Algorithm Simulator

Web-based algorithm visualization platform built on a clean 3-layer architecture:

**Architecture Layers:**
- **Routers** (HTTP controllers in backend/routers/)
- **Services** (business logic: algorithm implementations in services/)
- **Data** (persistence: repositories and schema in data/)

**Frontend:** React + Konva canvas + FastAPI backend

## Features

- Binary Search Tree (insert, delete, traversals, step animation)
- General Tree traversal visualization
- Hash table visualization and operations
- Recursion tree simulation
- Database management and reporting helpers
- Plugin-ready frontend algorithm registry for future extensions

## Tech Stack

- Python 3.12+
- FastAPI + Uvicorn
- React 18 + Vite + Zustand + Konva.js
- SQLite
- pytest / unittest

## Project Structure

- backend/: FastAPI app and HTTP routers (BST, AVL, B-Tree, B+ Tree, RB Tree, Hash, Recursion)
- services/: business logic layer (canonical algorithm implementations)
- data/: repositories and schema layer (SQLite persistence)
- frontend/: React + Vite simulator client with canvas visualizations
- tests/: automated tests

## Local Development

### 1. Backend setup

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run web backend

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 3. Run web frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 (frontend) and http://localhost:8000/api (FastAPI).

## Testing

```powershell
pytest -q
```

Alternative:

```powershell
python -m unittest discover -s tests -v
```

## Docker (Single Dockerfile)

This repository uses one root Dockerfile that:

- builds the React frontend
- installs Python backend dependencies
- serves API + built frontend from FastAPI on port 8000

Build:

```powershell
docker build -t visual-algorithm-simulator .
```

Run:

```powershell
docker run --rm -p 8000:8000 visual-algorithm-simulator
```

Open http://localhost:8000.

Optional with compose:

```powershell
docker compose up --build
```

## Debug Mode

Debug mode shows JSON state panels for inspecting algorithm state. By default, Debug mode is **hidden** from users.

**Activate Debug Mode:**
- Press `Ctrl + Shift + D` in the browser to reveal the **Debug On/Off** button
- Click to toggle debug panel visibility
- Press `Ctrl + Shift + D` again or click the button to deactivate

Debug state is persisted in browser localStorage.

## Extending Algorithms (Plugin Registry)

Frontend algorithms are registered through the registry module.
To add a new simulator (for example AVL or Dijkstra), register a new algorithm config and provide:

- load action
- render component
- optional traversal/playback behavior

## License

This project is licensed under the MIT License. See LICENSE for details.

