#!/usr/bin/env python3
"""
FastAPI server for Comic Generation System

Provides REST API endpoints for the React frontend to generate comics.
"""

import os
import sys
from typing import Optional
from pathlib import Path
import uuid
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import your existing comic generation classes
from src.services.config_service import ConfigService
from src.services.script_generator import ScriptGeneratorService
from src.services.script_parser import ScriptParserService
from src.services.image_generator import ImageGeneratorService
from src.services.comic_assembler import ComicAssemblerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Comic Generator API",
    description="Generate comics from historical events using AI",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (generated comics)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

class ComicRequest(BaseModel):
    event: str
    style: Optional[str] = "amar_chitra_katha"

class ComicResponse(BaseModel):
    success: bool
    comic_path: Optional[str] = None
    comic_url: Optional[str] = None
    error: Optional[str] = None
    task_id: Optional[str] = None

class ComicGenerator:
    """Comic generation service wrapper for FastAPI."""
    
    def __init__(self):
        """Initialize the comic generator with all required services."""
        try:
            self.config = ConfigService()
            self.script_generator = ScriptGeneratorService(self.config)
            self.script_parser = ScriptParserService()
            self.image_generator = ImageGeneratorService(self.config)
            self.comic_assembler = ComicAssemblerService(self.config)
            logger.info("Comic generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize comic generator: {e}")
            raise

    def generate_comic(self, event_description: str, style: Optional[str] = None) -> str:
        """
        Generate a complete comic from an event description.
        
        Args:
            event_description: Description of the event to create a comic about
            style: Optional comic style (defaults to config setting)
            
        Returns:
            Path to the generated comic file
        """
        logger.info(f"Starting comic generation for: {event_description}")
        
        try:
            # Step 1: Generate script
            logger.info("Generating comic script...")
            script_text = self.script_generator.generate_script(event_description, style)
            logger.info("Script generated successfully")
            
            # Step 2: Parse script into panels
            logger.info("Parsing script into panels...")
            comic_style = style or self.config.get_comic_style()
            script = self.script_parser.parse_script(script_text, event_description, comic_style)
            logger.info(f"Parsed {script.panel_count} panels")
            
            # Step 3: Generate images for all panels
            logger.info(f"Generating images for {script.panel_count} panels...")
            self.image_generator.generate_all_panel_images(
                script, 
                progress_callback=lambda msg: logger.info(f"Image generation: {msg}")
            )
            
            # Step 4: Assemble final comic
            logger.info("Assembling final comic...")
            comic = self.comic_assembler.assemble_comic(script)
            logger.info(f"Comic assembled: {comic.output_path}")
            
            return comic.output_path
            
        except Exception as e:
            logger.error(f"Error generating comic: {e}")
            raise

# Initialize the comic generator
try:
    generator = ComicGenerator()
except Exception as e:
    logger.error(f"Failed to initialize comic generator: {e}")
    sys.exit(1)

# In-memory storage for task status (in production, use Redis or database)
tasks = {}

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Comic Generator API is running"}

@app.post("/api/generate-comic", response_model=ComicResponse)
async def generate_comic_endpoint(request: ComicRequest, background_tasks: BackgroundTasks):
    """
    Generate a comic from event description and style.
    """
    if not request.event.strip():
        raise HTTPException(status_code=400, detail="Event description is required")
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Initialize task status
    tasks[task_id] = {
        "status": "started",
        "progress": "Initializing comic generation...",
        "error": None,
        "result": None
    }
    
    # Start comic generation in background
    background_tasks.add_task(
        generate_comic_background,
        task_id,
        request.event,
        request.style
    )
    
    return ComicResponse(
        success=True,
        task_id=task_id
    )

async def generate_comic_background(task_id: str, event: str, style: Optional[str]):
    """Background task for comic generation."""
    try:
        tasks[task_id]["status"] = "generating"
        tasks[task_id]["progress"] = "Generating comic script and images..."
        
        # Generate the comic
        comic_path = generator.generate_comic(event, style)
        
        # Copy to static directory for serving
        static_filename = f"comic_{task_id}.png"
        static_path = os.path.join("static", static_filename)
        
        # Copy the generated comic to static directory
        import shutil
        shutil.copy2(comic_path, static_path)
        
        # Update task status
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = "Comic generated successfully!"
        tasks[task_id]["result"] = {
            "comic_path": static_path,
            "comic_url": f"/static/{static_filename}"
        }
        
    except Exception as e:
        logger.error(f"Error in background comic generation: {e}")
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a comic generation task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] == "completed":
        return {
            "status": "completed",
            "success": True,
            "comic_url": task["result"]["comic_url"],
            "progress": task["progress"]
        }
    elif task["status"] == "error":
        return {
            "status": "error",
            "success": False,
            "error": task["error"]
        }
    else:
        return {
            "status": task["status"],
            "success": False,
            "progress": task["progress"]
        }

@app.get("/api/generate-comic-sync", response_model=ComicResponse)
async def generate_comic_sync(event: str, style: Optional[str] = "amar_chitra_katha"):
    """
    Synchronous comic generation endpoint (for testing).
    """
    if not event.strip():
        raise HTTPException(status_code=400, detail="Event description is required")
    
    try:
        # Generate the comic
        comic_path = generator.generate_comic(event, style)
        
        # Copy to static directory for serving
        static_filename = f"comic_{uuid.uuid4()}.png"
        static_path = os.path.join("static", static_filename)
        
        # Copy the generated comic to static directory
        import shutil
        shutil.copy2(comic_path, static_path)
        
        comic_url = f"/static/{static_filename}"
        
        return ComicResponse(
            success=True,
            comic_path=static_path,
            comic_url=comic_url
        )
        
    except Exception as e:
        logger.error(f"Error generating comic: {e}")
        return ComicResponse(
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )