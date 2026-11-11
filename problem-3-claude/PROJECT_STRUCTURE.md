# Video to 3D Model to Explainer Video - Project Structure

## Overview
Healthcare product visualization platform solving flat photos, slow production, and expensive changes.

## Folder Structure

```
/Users/vaishnavipatange/Downloads/claude/
├── frontend/              # Next.js frontend
│   ├── app/
│   │   ├── page.tsx       # Landing page
│   │   ├── upload/page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── package.json
│   └── README.md
│
└── backend/               # Python FastAPI backend
    ├── app.py             # Main FastAPI app
    ├── requirements.txt   # Python dependencies
    ├── .env              # Environment variables
    ├── .env.example
    ├── uploads/          # Uploaded media storage
    ├── outputs/          # Generated 3D models & videos
    └── README.md
```

## Setup Instructions

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

### Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# http://localhost:8000
```

## API Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `POST /api/upload` - Upload files
- `POST /api/process/3d-model` - Start 3D processing
- `GET /api/projects/{id}/status` - Project status

## Problem Statement
Healthcare companies need clear product visualization:
- Flat & heavy: Photos and demo kits
- Slow to produce: Weeks + agency
- Expensive to change: Scanner/CAD expert needed

## Solution
Turn phone videos/photos → 3D model → Explainer video
