# Architecture & System Flow: Video to 3D Model to Explainer Video

## 1. Executive Summary & Problem Addressed
Healthcare companies face significant bottlenecks in product visualization:
- **Flat & Heavy:** Relying on flat 2D photos and physical demo kits.
- **Slow to Produce:** Explainer videos take weeks and expensive external agencies.
- **Expensive to Change:** 3D models require costly scanners, CAD experts, and starting over for every language, finish, or audience change.

**Solution:** An end-to-end automated pipeline that turns a simple phone video or photo set into an interactive **3D Model** and a professional **Explainer Video**.

---

## 2. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│                      Next.js 15 App                         │
│  - Landing Page (`/`)                                       │
│  - Upload Flow (`/upload`)                                  │
│  - Project Status & 3D Viewer (`/projects/[id]`)            │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
        HTTP / FormData                 HTTP / JSON
               │                              │
               ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│                      Python FastAPI                         │
│                                                             │
│  - API Endpoints (`app.py`)                                 │
│  - Pydantic Models (`models.py`)                            │
│                                                             │
│  ┌───────────────────────┐         ┌─────────────────────┐  │
│  │ 3D Reconstruction     │         │ Explainer Video     │  │
│  │ Module                │         │ Generator           │  │
│  │ (OpenCV + Trimesh)    │         │ (MoviePy + PIL)     │  │
│  └───────────────────────┘         └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Frontend Architecture (`/frontend`)

### Technology Stack
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **3D Graphics:** React Three Fiber (`@react-three/fiber`), Three.js (`three`), `@react-three/drei`
- **HTTP Client:** Native `fetch` / Axios

### Directory & Component Breakdown
```
frontend/
├── app/
│   ├── layout.tsx                # Root layout (Inter font, dark/light mode)
│   ├── page.tsx                  # Landing page (Value prop & pain points)
│   ├── upload/
│   │   └── page.tsx              # Media upload & project creation form
│   └── projects/
│       └── [id]/
│           └── page.tsx          # Real-time progress tracker, 3D viewer & video trigger
├── components/
│   └── ModelViewer.tsx           # React Three Fiber 3D canvas with orbit controls
├── lib/
│   └── api.ts                    # API service wrapper for FastAPI backend
└── package.json                  # Dependencies (next, react, three, @react-three/fiber)
```

### Frontend Data Flow
1. **User Input (`/upload`):** User enters product name, type (implant, instrument), description, and selects media (video file or multiple photos).
2. **Project Initialization (`lib/api.ts`):**
   - Calls `POST /api/projects` to create project ID.
   - Calls `POST /api/upload` with `FormData` containing media files.
   - Calls `POST /api/process/3d-model` to trigger background reconstruction.
   - Redirects user to `/projects/[id]`.
3. **Status Polling (`/projects/[id]`):** Polls `GET /api/projects/{id}/status` every 3 seconds to update step progress.
4. **Interactive Rendering:** Once complete, renders the 3D model in `ModelViewer.tsx` and allows triggering the explainer video generation (`POST /api/generate/explainer-video`).

---

## 4. Backend Architecture (`/backend`)

### Technology Stack
- **Framework:** FastAPI (Python 3.9+)
- **Server:** Uvicorn (ASGI)
- **3D / Computer Vision:** OpenCV (`cv2`), NumPy, Trimesh, SciPy
- **Video Processing:** MoviePy, Pillow (`PIL`)
- **Data Validation:** Pydantic & Pydantic Settings

### Directory Breakdown
```
backend/
├── app.py                        # FastAPI application & background task orchestrator
├── models.py                     # Pydantic data models & enums
├── requirements.txt              # Python package dependencies
├── .env                          # Environment configuration
├── processing/
│   ├── reconstruction.py         # Photogrammetry pipeline (SIFT, camera poses, mesh)
│   └── explainer_video.py        # Multi-scene video composition (MoviePy)
├── uploads/                      # Raw uploaded media per project
└── outputs/
    ├── models/                   # Generated 3D models (.obj, .glb, metadata)
    └── videos/                   # Generated explainer videos (.mp4)
```

---

## 5. Detailed Pipeline Flow

### Phase 1: Ingestion & Upload
- **Endpoint:** `POST /api/upload`
- **Process:** Validates file extensions (`.mp4`, `.mov`, `.jpg`, `.png`), saves files to `./uploads/{project_id}/`, and registers project status as `uploading`.

### Phase 2: 3D Reconstruction (`processing/reconstruction.py`)
- **Trigger:** `POST /api/process/3d-model` (runs in background thread).
- **Steps:**
  1. **Frame Extraction:** If input is a video, OpenCV extracts key frames (up to 30 frames).
  2. **Feature Detection:** SIFT (`cv2.SIFT_create()`) detects distinctive keypoints and computes descriptors across all images.
  3. **Feature Matching:** BFMatcher matches features between consecutive views.
  4. **Pose Estimation & Triangulation:** Estimates fundamental matrix, camera poses, and triangulates 3D points.
  5. **Mesh Generation:** Converts the point cloud into a 3D triangle mesh using Delaunay triangulation / Trimesh.
  6. **Export:** Saves the model as `.obj` and `.glb` in `./outputs/models/`.

### Phase 3: Explainer Video Generation (`processing/explainer_video.py`)
- **Trigger:** `POST /api/generate/explainer-video` (runs in background thread).
- **Steps:**
  1. **Title Scene:** Generated using PIL & MoviePy with product title, subtitle, and branding.
  2. **3D Model Scene:** Renders rotating 3D visualization / wireframe representation.
  3. **Annotation Scenes:** Highlights key product features with callouts, descriptions, and pointer graphics.
  4. **Specifications Scene:** Renders medical grade, sterilization, and compatibility specs.
  5. **Closing Scene:** Adds call-to-action / QR code prompt.
  6. **Rendering:** Combines clips into a 1080p HD `.mp4` video using H.264 codec and saves to `./outputs/videos/`.

---

## 6. API Reference Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service root and status |
| `GET` | `/health` | Storage and service health check |
| `POST` | `/api/projects` | Create a new visualization project |
| `GET` | `/api/projects` | List all projects |
| `POST` | `/api/upload` | Upload video or photos for a project |
| `POST` | `/api/process/3d-model` | Start background 3D reconstruction |
| `POST` | `/api/generate/explainer-video` | Start background video generation |
| `GET` | `/api/projects/{id}/status` | Get live progress & step status |
| `GET` | `/api/projects/{id}/model` | Download generated 3D model path/metadata |
| `GET` | `/api/projects/{id}/video` | Get generated explainer video path/metadata |
