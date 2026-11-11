from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router as instrument_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for ZED 2i / Phone Video -> 3D Surgical Instrument (.glb) -> Automated Explainer Video (.mp4)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instrument_router, prefix="/api/v1", tags=["Surgical Instruments 3D Pipeline"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "zed_2i_pipeline": "ready",
        "sam2_segmentation": "ready",
        "open3d_tsdf_mesh": "ready",
        "headless_blender_explainer": "ready"
    }
