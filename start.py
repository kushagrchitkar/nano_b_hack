#!/usr/bin/env python3
"""
Startup script to run both FastAPI backend and React frontend
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies found")
    except ImportError:
        print("❌ FastAPI not found. Please run: pip install fastapi uvicorn python-multipart")
        return False
    
    # Check if Node.js is available
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js/npm found (version: {result.stdout.strip()})")
        else:
            print("❌ npm not found. Please install Node.js")
            return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js")
        return False
    
    return True

def start_fastapi():
    """Start the FastAPI server in the background."""
    print("🚀 Starting FastAPI server...")
    return subprocess.Popen([
        sys.executable, "api_server.py"
    ], cwd=Path.cwd())

def start_react():
    """Start the React development server."""
    frontend_path = Path.cwd() / "frontend"
    
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return None
    
    print("🚀 Starting React development server...")
    return subprocess.Popen([
        "npm", "start"
    ], cwd=frontend_path)

def main():
    print("🎬 Comic Generator - Starting Development Environment")
    print("=" * 60)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Start FastAPI backend
    fastapi_process = start_fastapi()
    if not fastapi_process:
        print("❌ Failed to start FastAPI server")
        sys.exit(1)
    
    # Wait a moment for FastAPI to start
    time.sleep(2)
    
    # Start React frontend
    react_process = start_react()
    if not react_process:
        print("❌ Failed to start React server")
        fastapi_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Both servers started successfully!")
    print("📱 React frontend: http://localhost:3000")
    print("🔧 FastAPI backend: http://localhost:8001")
    print("📚 API docs: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Wait for both processes
        fastapi_process.wait()
        react_process.wait()
    except KeyboardInterrupt:
        print("\n⏹️ Shutting down servers...")
        react_process.terminate()
        fastapi_process.terminate()
        
        # Wait for clean shutdown
        react_process.wait()
        fastapi_process.wait()
        
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()