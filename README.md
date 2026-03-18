# Visual Algorithm Simulator

Visual Algorithm Simulator is a desktop app for exploring and editing core data structures.
It uses a layered architecture (presentation -> services -> data), with a Tkinter UI and SQLite persistence.

## Features

- Hash table visualization and chaining operations
- Recursion call-tree visualization
- Integrated CRUD in Visual Studio (add, update, delete across structures)
- General tree and Binary Search Tree (BST) step-based traversal simulation
- Animated traversal/export workflow (GIF/MP4)
- SQL export/import and HTML state report generation

## Tech Stack

- Python 3.x
- Tkinter (GUI)
- SQLite
- unittest / pytest
- Pillow, imageio, imageio-ffmpeg (capture/export)

## Project Structure

- app.py: application entry point
- presentation/: GUI layer
- services/: application/service layer
- data/: repository and schema layer
- tests/: automated tests
- izvjestaji/: generated HTML reports

## Local Setup

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## Testing

```powershell
pytest -q
```

Alternative without pytest:

```powershell
python -m unittest discover -s tests -v
```

## Docker

Build image:

```powershell
docker build -t visual-algorithm-simulator .
```

Run tests in container:

```powershell
docker run --rm visual-algorithm-simulator
```

Run another command (example):

```powershell
docker run --rm -it visual-algorithm-simulator python app.py
```

Note: Running Tkinter GUI in Docker requires additional display setup (X11/WSLg). For local GUI work, run on the host machine.

## Architecture Notes

- The presentation layer does not access the database directly.
- The services layer provides a stable API for GUI and tests.
- The data layer owns SQL operations and data integrity rules.

## UI Notes

- Visual Studio is the primary user workflow.
- CRUD actions are available directly from the Visual Studio sidebar.

## License

This project is licensed under the MIT License. See LICENSE for details.

