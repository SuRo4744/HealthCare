"""
Pydantic models for API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    SCAN = "scan"
    MODEL = "model"


class ProjectStatus(str, Enum):
    CREATED = "created"
    UPLOADING = "uploading"
    PROCESSING_3D = "processing_3d"
    GENERATING_VIDEO = "generating_video"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    product_type: Optional[str] = Field(None, max_length=100)
    target_audience: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field("en", max_length=5)


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    product_type: Optional[str]
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    progress: float = 0.0
    steps: List[Dict[str, Any]]


class UploadResponse(BaseModel):
    project_id: str
    uploaded: List[Dict[str, Any]]
    count: int
    total_size: int


class ReconstructionRequest(BaseModel):
    project_id: str
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ReconstructionResponse(BaseModel):
    project_id: str
    task_id: str
    status: str
    message: str
    estimated_time: str


class ModelMetadata(BaseModel):
    project_id: str
    model_path: str
    format: str
    point_count: int
    triangle_count: int
    bounding_box: Optional[List[float]]
    created_at: datetime
    reconstruction_method: str


class ExplainerVideoRequest(BaseModel):
    project_id: str
    product_name: str
    product_type: str
    language: str = "en"
    features: Optional[List[Dict[str, str]]] = None
    specs: Optional[Dict[str, str]] = None


class ExplainerVideoResponse(BaseModel):
    project_id: str
    video_path: str
    duration: float
    status: str
    metadata: Dict[str, Any]


class ProjectStatusResponse(BaseModel):
    id: str
    status: ProjectStatus
    progress: float
    steps: List[Dict[str, Any]]
    updated_at: datetime
    artifacts: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, bool]
    version: str
