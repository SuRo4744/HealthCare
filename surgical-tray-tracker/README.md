# SurgTrace AI: Surgical Instrument Tray Tracking & Missing Item Detection
### Next.js 15 Frontend + Python FastAPI Backend + YOLOv8/Roboflow Computer Vision

## 1. Problem Statement Addressed
Hospitals face severe operational and patient-safety risks during surgical procedures regarding instrument tray management:
- **Retained or Missing Instruments:** Surgical counts are currently performed manually by nurses under immense time pressure, risking retained surgical items (RSIs) or missing components before closure.
- **Hidden Waste & Sterilization Inefficiencies:** Hospitals lack visibility into actual instrument utilization, often repeatedly sterilizing entire trays where 30-40% of the tools are never touched.
- **Solution:** An automated computer vision tracking pipeline that ingests operating room back-table camera feeds, detects and classifies every instrument, tracks tray inventory in real-time, and flags missing or retained items instantly.

---

## 2. System Architecture

```text
+---------------------------------------------------------------------------------------------------+
| TIER 1: MULTI-MODAL CAPTURE LAYER (OR Back-Table & Tray Feeds)                                    |
|  +-- Operating Room Overhead / Tray Camera Feed (RTSP / WebRTC / 4K Video)                        |
|  +-- Public Kaggle / Roboflow Surgical Instrument Datasets + Custom Hand Tool / Dissection Kits   |
+-------------------------------------------------+-------------------------------------------------+
                                                  | (Chunked Upload / Presigned HTTP Stream)
                                                  v
+---------------------------------------------------------------------------------------------------+
| TIER 2: FRONTEND - Next.js 15 (App Router, TypeScript, Tailwind CSS)                              |
|  +-- Real-Time Tray Dashboard: Live inventory matrix (Present, In-Use, Missing)                   |
|  +-- Bounding Box Video Streamer & Alert Banner for Missing Items                                 |
|  +-- Utilization Analytics Tab: Heatmaps showing unused tools for tray optimization               |
+-------------------------------------------------+-------------------------------------------------+
                                                  | (REST API + WebSockets Live Telemetry)
                                                  v
+---------------------------------------------------------------------------------------------------+
| TIER 3: BACKEND API GATEWAY - Python FastAPI                                                      |
|  +-- /api/v1/tray/upload       (Ingests OR video recording or tray snapshot photo)                |
|  +-- /api/v1/tray/{id}/detect  (Dispatches YOLOv8 inference pipeline)                             |
|  +-- /api/v1/tray/{id}/ws      (Real-time missing item alert stream)                              |
+-------------------------------------------------+-------------------------------------------------+
                                                  | (Redis Broker + Celery Worker Queue)
                                                  v
+---------------------------------------------------------------------------------------------------+
| TIER 4: COMPUTER VISION INFERENCE ENGINE (YOLOv8 / Roboflow API / OpenCV)                         |
|  1. Tray Grid Localization & ROI Masking: Identifies silhouette slots on the metal sterilization tray|
|  2. Instrument Detection & Bounding Boxes: Detects scalpel, forceps, needle holder, clamp, retractor|
|  3. Count Reconciliation: Compares pre-op baseline tray count vs current tray count                 |
|  4. Missing / Retained Item Alert Engine: Triggers high-priority visual/audio alert if mismatch    |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Repository Structure

```text
surgical-tray-tracker/
├── docker-compose.yml              # Orchestrates FastAPI, Next.js, Redis, and Celery Worker
├── README.md                       # Architecture & Setup Guide
├── backend/                        # Python FastAPI Backend & CV Inference Engine
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # FastAPI application entry point, CORS, WebSockets
│       ├── config.py               # Environment configuration settings
│       ├── models/
│       │   └── schemas.py          # Pydantic data schemas for tray inventory and detection
│       ├── api/
│       │   └── routes.py           # Endpoints for tray upload, detection, and analytics
│       └── services/
│           └── detector.py         # YOLOv8 / OpenCV surgical instrument detection & counting logic
└── frontend/                       # Next.js 15 Dashboard Frontend
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── next.config.mjs
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── globals.css
        │   └── page.tsx            # Live Tray Inventory Matrix, Missing Item Alerts, Analytics
        └── types/
            └── tray.ts             # TypeScript interfaces matching FastAPI schemas
```

---

## 4. Quick Start Guide (Local Laptop Setup)

### Option A: Run FastAPI Backend & Next.js Frontend Directly

#### 1. Start the Python FastAPI Backend
```bash
cd backend
python3 -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*API documentation and Swagger UI will be available at `http://localhost:8000/docs`.*

#### 2. Start the Next.js Frontend
Open a second terminal tab:
```bash
cd frontend
npm install
npm run dev
```
*Open `http://localhost:3000` in your browser to view the live surgical tray tracking dashboard.*

### Option B: Run Full Stack with Docker Compose
```bash
docker-compose up --build
```
