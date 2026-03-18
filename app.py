"""
Visual Algorithm Simulator - Main Entry Point
Choose between Desktop (Tkinter) or Web (React + FastAPI) interfaces
"""
import subprocess
import sys
import time
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from presentation.gui import build_ui


def start_desktop_app():
    """Launch Tkinter desktop application"""
    try:
        root = build_ui()
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Desktop App Error", f"Failed to start desktop app:\n{e}")
        sys.exit(1)


def start_web_app():
    """Launch FastAPI backend + open React frontend in browser"""
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Start FastAPI server in background
        print("🚀 Starting FastAPI backend on http://localhost:8000...")
        backend_process = subprocess.Popen(
            [sys.executable, str(backend_dir / "main.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(backend_dir)
        )
        
        # Wait for backend to start
        time.sleep(3)
        
        # Check if backend started successfully
        if backend_process.poll() is not None:
            raise RuntimeError("Backend failed to start. Check logs above.")
        
        print("✓ Backend started successfully")
        
        # Open browser to frontend (Vite dev server should already be running)
        print("🌐 Opening frontend in browser...")
        webbrowser.open("http://localhost:3000")
        
        print("\n" + "="*60)
        print("Frontend: http://localhost:3000")
        print("Backend:  http://localhost:8000")
        print("API Docs: http://localhost:8000/docs")
        print("="*60)
        print("\nPress Ctrl+C to stop...\n")
        
        # Keep process running
        backend_process.wait()
        
    except Exception as e:
        messagebox.showerror("Web App Error", f"Failed to start web app:\n{e}")
        sys.exit(1)
    finally:
        print("\n✗ Application terminated")


def show_menu():
    """Display startup menu in Tkinter window"""
    root = tk.Tk()
    root.title("Algorithm Simulator - Startup Menu")
    root.geometry("400x250")
    root.resizable(False, False)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")
    
    # Title
    title = tk.Label(
        root,
        text="🎨 Algorithm Simulator",
        font=("Arial", 18, "bold"),
        fg="#2563eb"
    )
    title.pack(pady=20)
    
    # Description
    desc = tk.Label(
        root,
        text="Choose your interface:",
        font=("Arial", 11),
        fg="#6b7280"
    )
    desc.pack(pady=10)
    
    # Desktop Button
    def on_desktop():
        root.destroy()
        start_desktop_app()
    
    desktop_btn = tk.Button(
        root,
        text="💻 Desktop (Tkinter)",
        command=on_desktop,
        font=("Arial", 12, "bold"),
        bg="#10b981",
        fg="white",
        padx=20,
        pady=15,
        relief=tk.RAISED,
        cursor="hand2"
    )
    desktop_btn.pack(pady=10, padx=20, fill=tk.X)
    
    # Web Button
    def on_web():
        root.destroy()
        start_web_app()
    
    web_btn = tk.Button(
        root,
        text="🌐 Web (React + FastAPI)",
        command=on_web,
        font=("Arial", 12, "bold"),
        bg="#2563eb",
        fg="white",
        padx=20,
        pady=15,
        relief=tk.RAISED,
        cursor="hand2"
    )
    web_btn.pack(pady=10, padx=20, fill=tk.X)
    
    # Exit Button
    exit_btn = tk.Button(
        root,
        text="Exit",
        command=root.quit,
        font=("Arial", 10),
        bg="#ef4444",
        fg="white",
        padx=20,
        pady=10
    )
    exit_btn.pack(pady=10, padx=20, fill=tk.X)
    
    root.mainloop()


if __name__ == "__main__":
    show_menu()