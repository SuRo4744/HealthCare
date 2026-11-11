# SURG-3D: Video-to-3D Surgical Instrument & Explainer Pipeline
### ZED 2i Stereo Camera / Phone Video -> Accurate 3D Instrument Model (.glb / .splat) -> Automated Explainer Video (.mp4)

## 1. Problem Statement Addressed
Healthcare companies, surgical trainers, and sales reps struggle to digitize hundreds of orthopedic surgical instruments (such as **Tibial Cutting Guides, Femoral Sizers, Bone Rongeurs, and Intramedullary Rods** used in Total Knee Arthroplasty):
- **Flat & Heavy:** Physical instrument trays weigh 10–15 kg and flat 2D photos fail to show slot tolerances or locking mechanisms.
- **Slow to Produce:** Training videos for scrub nurses and surgeons take weeks and external agencies to produce.
- **Expensive to Change:** Re-scanning or hiring a CAD expert for every new surface finish (e.g., Satin Stainless Steel vs. TiN Gold Coating vs. Matte PEEK), new language, or new audience (Surgeon vs. Scrub Nurse vs. Patient) is cost-prohibitive.

---

## 2. End-to-End System Architecture (Surgical Instrument Focus)

```text
+---------------------------------------------------------------------------------------------------+
| TIER 1: MULTI-MODAL CAPTURE LAYER (OR Back-Table & Benchtop)                                      |
|  +-- ZED 2i Stereo Camera (Polarizer): Captures .svo2 (Stereo RGB + Neural Plus Depth + 6-DoF IMU)|
|  +-- Smartphone Video / Photos: Captures 30-60s 4K .mp4 orbit around surgical instrument          |
+-------------------------------------------------+-------------------------------------------------+
                                                  | (Chunked Upload / Presigned S3 URL)
                                                  v
+---------------------------------------------------------------------------------------------------+
| TIER 2: FRONTEND - Next.js 15 (App Router, TypeScript, Tailwind CSS)                              |
|  +-- React Three Fiber (R3F) + Three.js: Interactive 3D Instrument Studio (.glb & Gaussian Splat) |
|  +-- Zero-Cost Material Swapper: Instant PBR Shader toggle (Stainless, TiN Gold, Anodized Blue)   |
|  +-- 3D Sub-Component Pinning & Exploded View Slider (Locking Dial, 1.2mm Saw Slot, Pin Holes)    |
|  +-- Explainer Video Director: Select Audience (Nurse/Surgeon/Sales), Language, & Keyframes       |
+-------------------------------------------------+-------------------------------------------------+
                                                  | (REST API + WebSockets Live Telemetry)
                                                  v
+---------------------------------------------------------------------------------------------------+
| TIER 3: BACKEND API GATEWAY - Python FastAPI                                                      |
|  +-- /api/v1/instruments/upload       (Ingests ZED 2i .svo2 or Phone .mp4)                        |
|  +-- /api/v1/instruments/{id}/reconstruct (Dispatches async Celery GPU reconstruction pipeline)   |
|  +-- /api/v1/instruments/{id}/explainer   (Dispatches Headless Blender + TTS video render)        |
|  +-- /api/v1/instruments/{id}/ws          (Real-time progress streaming to Next.js UI)            |
+-------------------------------------------------+-------------------------------------------------+
                                                  | (Redis Broker + Celery Task Queue)
                                                  v
+---------------------------------------------------------------------------------------------------+
| TIER 4: GPU COMPUTE WORKER PIPELINE (CUDA / PyTorch / Open3D / Blender)                           |
|  1. Frame & Depth Extraction:                                                                     |
|     - ZED 2i Path: pyzed SDK extracts Left RGB + 16-bit Metric Depth + 6-DoF Pose (No COLMAP!)    |
|     - Phone Path: FFmpeg extracts keyframes + COLMAP / GLOMAP estimates camera poses              |
|  2. Surgical Instrument Segmentation (SAM 2):                                                     |
|     - Isolates metallic instrument from green surgical drapes, trays, and gloved hands            |
|  3. Specular-Aware 3D Reconstruction:                                                             |
|     - Open3D TSDF Volume Fusion -> Metric-accurate watertight .glb mesh (accurate to <0.5mm)      |
|     - Depth-Regularized 3D Gaussian Splatting (gsplat / SuGaR) -> Captures metallic reflections   |
|  4. Automated Explainer Video Engine (Stretch Goal):                                              |
|     - LLM Script + Multi-lingual TTS (English, Hindi, Spanish) + Headless Blender (bpy) + FFmpeg  |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Repository Structure

```text
surg3d-instrument-pipeline/
├── docker-compose.yml                  # Orchestrates FastAPI, Next.js, Redis, Celery Worker, MinIO S3
├── README.md                           # Architecture & Setup Guide
├── docs/
│   └── ARCHITECTURE.md                 # Deep-dive technical architecture & Mermaid diagrams
├── backend/                            # Python FastAPI + GPU Worker Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py                     # FastAPI entry point, CORS, REST & WebSocket routes
│       ├── config.py                   # Environment settings (Redis, S3, ZED SDK flags)
│       ├── models/
│       │   └── schemas.py              # Pydantic schemas for instruments, annotations & video jobs
│       ├── api/
│       │   └── routes.py               # Endpoints for Upload, 3D Reconstruction, Explainer Render
│       ├── worker/
│       │   └── celery_worker.py        # Asynchronous GPU task orchestrator
│       └── services/
│           ├── zed_extractor.py        # Extracts RGB + Neural Depth + Poses from ZED 2i .svo2
│           ├── sam2_segmenter.py       # Masks surgical instrument from OR drapes/gloves
│           ├── reconstruct_3d.py       # Open3D TSDF Mesh Fusion + 3D Gaussian Splatting
│           └── blender_explainer.py    # Headless Blender (bpy) script + TTS + FFmpeg MP4 generator
└── frontend/                           # Next.js 15 + React Three Fiber 3D Instrument Studio
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── next.config.mjs
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── globals.css
        │   └── page.tsx                # Main Dashboard: Upload, 3D Studio, Material Swap, Video Gen
        ├── components/
        │   ├── InstrumentViewer3D.tsx  # React Three Fiber 3D surgical instrument viewer + hotspots
        │   ├── PipelineTelemetry.tsx   # Live WebSocket progress bar & architecture status
        │   └── ExplainerStudio.tsx     # Stretch Goal: Audience/Language explainer video generator
        └── types/
            └── instrument.ts           # TypeScript interfaces matching FastAPI schemas
```

---

## 4. Quick Start Guide (Local Laptop Setup)

### Option A: Run Frontend & Backend Directly (Fastest for Development / Demo)

#### 1. Start the Python FastAPI Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*The FastAPI Swagger UI will be available at `http://localhost:8000/docs`.*
*(Note: If your laptop does not have a physical ZED 2i camera plugged in, the backend automatically runs in **Simulation / Fallback Mode** so you can test the full Next.js-to-FastAPI pipeline immediately).*

#### 2. Start the Next.js 15 Frontend
```bash
cd frontend
npm install
npm run dev
```
*Open `http://localhost:3000` in your browser to interact with the 3D Knee Surgical Instrument Studio, swap metallic finishes in real time, inspect 3D hotspots, and trigger automated explainer video renders.*

### Option B: Run Full Stack with Docker Compose
```bash
docker-compose up --build
```
