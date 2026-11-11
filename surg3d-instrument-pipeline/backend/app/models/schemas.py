from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class HotspotAnnotation(BaseModel):
    id: str
    title: str
    description: str
    sub_component: str
    position_xyz: List[float] = Field(..., description="[x, y, z] coordinates in meters")
    camera_orbit: List[float] = Field(..., description="[azimuth, polar, distance]")

class InstrumentDimensions(BaseModel):
    length_mm: float
    width_mm: float
    height_mm: float
    saw_slot_tolerance_mm: float

class ExplainerRequest(BaseModel):
    audience: Literal["scrub_nurse", "surgeon", "sales_rep", "patient"] = "scrub_nurse"
    language: Literal["en-US", "hi-IN", "es-ES", "de-DE"] = "en-US"
    finish_override: Literal["satin_stainless", "tin_gold", "oxidized_black", "anodized_blue"] = "satin_stainless"
    include_exploded_view: bool = True
    camera_keyframes: Optional[List[List[float]]] = None

class ExplainerVideoOutput(BaseModel):
    job_id: str
    audience: str
    language: str
    finish_used: str
    script_narration: str
    video_url: str
    subtitles_url: str
    duration_sec: int

class InstrumentProject(BaseModel):
    instrument_id: str
    name: str
    category: str
    capture_source: Literal["ZED_2I_STEREO_SVO2", "PHONE_MULTIVIEW_MP4"]
    status: Literal["UPLOADED", "PROCESSING_3D", "READY_3D", "RENDERING_VIDEO", "COMPLETED"]
    progress_pct: int
    current_stage: str
    mesh_glb_url: Optional[str] = None
    gaussian_splat_url: Optional[str] = None
    dimensions: InstrumentDimensions
    hotspots: List[HotspotAnnotation]
    explainer_videos: List[ExplainerVideoOutput] = []
