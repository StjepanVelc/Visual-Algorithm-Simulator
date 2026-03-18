# Visual Algorithm Simulator

Visual Algorithm Simulator now supports two interfaces over the same core logic:

- Desktop UI (Tkinter)
- Web UI (React + Konva) with FastAPI backend

The project keeps a layered architecture:

- presentation -> services -> data

## Features

- Binary Search Tree (insert, delete, traversals, step animation)
- General Tree traversal visualization
- Hash table visualization and operations
- Recursion tree simulation
- Database management and reporting helpers
- Plugin-ready frontend algorithm registry for future extensions

## Tech Stack

- Python 3.x
- FastAPI + Uvicorn
- React + Vite + Zustand + React Konva
- Tkinter (desktop mode)
- SQLite
- pytest / unittest

## Project Structure

- app.py: desktop entry point
- backend/: FastAPI app and API routers
- frontend/: React simulator client
- services/: business logic layer
- data/: repositories and schema layer
- presentation/: desktop GUI modules
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

Open http://localhost:3000.

### 4. Run desktop app (optional)

```powershell
python app.py
```

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

## Extending Algorithms (Plugin Registry)

Frontend algorithms are registered through the registry module.
To add a new simulator (for example AVL or Dijkstra), register a new algorithm config and provide:

- load action
- render component
- optional traversal/playback behavior

## License

This project is licensed under the MIT License. See LICENSE for details.

