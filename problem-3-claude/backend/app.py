"""
FastAPI backend for Video to 3D Model to Explainer Video pipeline
Healthcare product visualization platform
"""

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from enum import Enum
import asyncio
import json

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import re
from pydantic_settings import BaseSettings

from models import (
    CreateProjectRequest, ProjectResponse, UploadResponse,
    ProjectStatusResponse, ReconstructionRequest, ReconstructionResponse,
    ExplainerVideoRequest, ExplainerVideoResponse, HealthResponse,
    FileType, ProjectStatus
)

# Create directories
UPLOAD_DIR = Path("./uploads")
OUTPUT_DIR = Path("./outputs")
DATA_DIR = Path("./data")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

PROJECTS_FILE = DATA_DIR / "projects.json"


def _serialize(obj):
    """Make project dicts JSON-safe (datetime -> isoformat, Path -> str)."""
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    if isinstance(obj, tuple):
        return [_serialize(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    return obj


def load_projects():
    """Load persisted projects from disk (survives uvicorn --reload)."""
    if PROJECTS_FILE.exists():
        try:
            with open(PROJECTS_FILE, "r") as f:
                data = json.load(f)
            for pid, proj in data.items():
                # Restore datetime fields
                for key in ("created_at", "updated_at"):
                    if isinstance(proj.get(key), str):
                        try:
                            proj[key] = datetime.fromisoformat(proj[key])
                        except ValueError:
                            pass
                projects_db[pid] = proj
        except Exception as e:
            print(f"Failed to load projects: {e}")


def save_projects():
    """Persist current projects to disk."""
    try:
        with open(PROJECTS_FILE, "w") as f:
            json.dump(_serialize(projects_db), f, indent=2, default=str)
    except Exception as e:
        print(f"Failed to save projects: {e}")


# In-memory project store (replace with DB in production)
projects_db = {}
processing_tasks = {}

# Load any projects persisted from a previous server run
load_projects()


class Settings(BaseSettings):
    app_name: str = "3D-Model-Pipeline"
    app_version: str = "0.1.0"
    debug: bool = True
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    max_upload_size_mb: int = 100

    class Config:
        env_file = ".env"


settings = Settings()


def process_3d_reconstruction_async(project_id: str):
    """Background task for 3D reconstruction"""
    try:
        project = projects_db.get(project_id)
        if not project:
            return

        project['status'] = ProjectStatus.PROCESSING_3D
        project['progress'] = 10
        project['updated_at'] = datetime.utcnow()
        save_projects()

        # Get uploaded files
        upload_dir = UPLOAD_DIR / project_id
        if not upload_dir.exists():
            project['status'] = ProjectStatus.FAILED
            project['progress'] = 0
            save_projects()
            return

        media_files = [f for f in upload_dir.glob("*") if f.is_file()]
        if not media_files:
            project['status'] = ProjectStatus.FAILED
            project['progress'] = 0
            save_projects()
            return

        project['progress'] = 30
        save_projects()

        # Import here to avoid circular imports
        from processing.reconstruction import reconstruct_project

        output_dir = OUTPUT_DIR / "models"
        result = reconstruct_project(project_id, media_files, output_dir)

        project['progress'] = 80
        project['artifacts'] = {
            'model_3d': str(result['model_path']),
            'metadata': result['metadata']
        }

        project['status'] = ProjectStatus.COMPLETED
        project['progress'] = 100
        project['steps'][1]['status'] = 'completed'
        project['steps'][1]['progress'] = 100
        project['updated_at'] = datetime.utcnow()
        save_projects()

    except Exception as e:
        print(f"Reconstruction failed: {e}")
        if project_id in projects_db:
            project = projects_db[project_id]
            project['status'] = ProjectStatus.FAILED
            project['progress'] = 0
            project['steps'][1]['status'] = 'failed'
            project['error'] = str(e)
            save_projects()


def generate_explainer_video_async(project_id: str):
    """Background task for explainer video generation"""
    try:
        project = projects_db.get(project_id)
        if not project:
            return

        project['status'] = ProjectStatus.GENERATING_VIDEO
        project['progress'] = 10
        project['updated_at'] = datetime.utcnow()
        save_projects()

        from processing.explainer_video import generate_explainer_for_project

        model_path = Path(project.get('artifacts', {}).get('model_3d', ''))
        if not model_path or not Path(model_path).exists():
            # Create dummy model path
            model_path = OUTPUT_DIR / "models" / f"{project_id}_model.obj"

        output_dir = OUTPUT_DIR / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)

        project['progress'] = 50

        result = generate_explainer_for_project(
            project_id=project_id,
            product_name=project['name'],
            product_type=project.get('product_type', 'Medical Device'),
            model_path=model_path,
            output_dir=output_dir
        )

        project['progress'] = 90
        project['artifacts']['explainer_video'] = result['video_path']
        project['artifacts']['video_metadata'] = result

        project['status'] = ProjectStatus.COMPLETED
        project['progress'] = 100
        project['steps'][2]['status'] = 'completed'
        project['steps'][2]['progress'] = 100
        project['updated_at'] = datetime.utcnow()
        save_projects()

    except Exception as e:
        print(f"Video generation failed: {e}")
        if project_id in projects_db:
            project = projects_db[project_id]
            project['status'] = ProjectStatus.FAILED
            project['progress'] = 0
            project['steps'][2]['status'] = 'failed'
            project['error'] = str(e)
            save_projects()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Healthcare product visualization pipeline - Video to 3D Model to Explainer Video"
)

# CORS middleware
# Allow localhost, 127.0.0.1, and private IP ranges (e.g. Next.js network URL http://192.168.x.x:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?",
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "projects": "/api/projects",
            "upload": "/api/upload"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "storage": UPLOAD_DIR.exists(),
            "output": OUTPUT_DIR.exists()
        },
        version=settings.app_version
    )


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    project_id = f"proj_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    project = {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "product_type": request.product_type,
        "status": ProjectStatus.CREATED,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "progress": 0.0,
        "steps": [
            {"name": "upload_media", "status": "pending", "description": "Upload video/photos", "progress": 0},
            {"name": "process_3d", "status": "pending", "description": "Generate 3D model", "progress": 0},
            {"name": "create_explainer", "status": "pending", "description": "Generate explainer video", "progress": 0},
        ],
        "artifacts": {}
    }

    projects_db[project_id] = project
    save_projects()

    return ProjectResponse(**project)


@app.get("/api/projects")
async def list_projects():
    projects = list(projects_db.values())
    return {
        "projects": projects,
        "total": len(projects)
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(
    project_id: str = Form(...),
    files: List[UploadFile] = File(...),
    file_type: str = Form("photo")
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    project_upload_dir = UPLOAD_DIR / project_id
    project_upload_dir.mkdir(exist_ok=True)

    uploaded = []
    total_size = 0

    for file in files:
        if not file.filename:
            continue

        ext = Path(file.filename).suffix.lower()
        allowed_extensions = {
            "photo": [".jpg", ".jpeg", ".png", ".webp"],
            "video": [".mp4", ".mov", ".avi"],
            "scan": [".stl", ".obj", ".glb", ".gltf"]
        }

        if ext not in allowed_extensions.get(file_type, []):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for {file_type}: {ext}"
            )

        filename = f"{datetime.utcnow().strftime('%H%M%S')}_{file.filename}"
        file_path = project_upload_dir / filename

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        uploaded.append({
            "filename": file.filename,
            "saved_as": filename,
            "size": len(content),
            "type": file_type
        })
        total_size += len(content)

    # Update project status
    projects_db[project_id]['status'] = ProjectStatus.UPLOADING
    projects_db[project_id]['progress'] = 20
    projects_db[project_id]['steps'][0]['status'] = 'completed'
    projects_db[project_id]['steps'][0]['progress'] = 100
    projects_db[project_id]['updated_at'] = datetime.utcnow()
    save_projects()

    return UploadResponse(
        project_id=project_id,
        uploaded=uploaded,
        count=len(uploaded),
        total_size=total_size
    )


@app.post("/api/process/3d-model", response_model=ReconstructionResponse)
async def generate_3d_model(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    project['steps'][1]['status'] = 'in_progress'
    project['steps'][1]['progress'] = 0

    task_id = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    background_tasks.add_task(process_3d_reconstruction_async, project_id)

    return ReconstructionResponse(
        project_id=project_id,
        task_id=task_id,
        status="processing",
        message="3D model generation started",
        estimated_time="5-10 minutes"
    )


@app.post("/api/generate/explainer-video", response_model=ExplainerVideoResponse)
async def generate_explainer_video(
    background_tasks: BackgroundTasks,
    request: ExplainerVideoRequest
):
    if request.project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[request.project_id]
    project['steps'][2]['status'] = 'in_progress'
    project['steps'][2]['progress'] = 0

    background_tasks.add_task(generate_explainer_video_async, request.project_id)

    return ExplainerVideoResponse(
        project_id=request.project_id,
        video_path="",
        duration=0.0,
        status="processing",
        metadata={"message": "Video generation started"}
    )


@app.get("/api/projects/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    return ProjectStatusResponse(**project)


@app.get("/api/projects/{project_id}/model")
async def get_3d_model(project_id: str, format: str = "obj"):
    """Download generated 3D model"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    model_path = project.get('artifacts', {}).get('model_3d')

    if not model_path:
        raise HTTPException(status_code=404, detail="Model not found")

    # Serve the actual model file so the frontend can render it directly.
    # model_path is stored without an extension; resolve the real file.
    base = Path(model_path)
    ext = format.lower()
    file_path = base.with_suffix(f".{ext}")
    if not file_path.exists():
        # Fall back to whatever model file exists next to the stored path
        for candidate in [base.with_suffix('.obj'),
                          base.with_suffix('.glb')]:
            if candidate.exists():
                file_path = candidate
                break

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Model file not found")

    return FileResponse(
        str(file_path),
        media_type="application/octet-stream",
        filename=file_path.name,
    )


@app.get("/api/projects/{project_id}/video")
async def get_explainer_video(project_id: str):
    """Get explainer video info"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    video_path = project.get('artifacts', {}).get('explainer_video')

    if not video_path:
        raise HTTPException(status_code=404, detail="Video not generated yet")

    # Serve the actual video file so the frontend can play it inline
    vp = Path(video_path)
    if not vp.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        str(vp),
        media_type="video/mp4",
        filename=vp.name,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug
    )
