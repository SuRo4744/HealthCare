# Frontend & Backend Connected

## Full Integration Complete

### Frontend Features
- **Upload Page (`/upload`)**: Allows entering product details, selecting file type (video or multiple photos), uploading files, and triggering 3D reconstruction.
- **Project Detail Page (`/projects/[id]`)**: Real-time project status polling, step progress tracker, interactive 3D model viewer with React Three Fiber, and explainer video generation trigger.
- **API Client (`/lib/api.ts`)**: Connects Next.js to FastAPI endpoints (`http://localhost:8000`).

### Backend Features
- FastAPI backend processing uploads, running SIFT photogrammetry 3D reconstruction, and generating MoviePy explainer videos.

## How to Run Together

1. **Start Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app:app --reload --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser:**
   Go to `http://localhost:3000` to view the landing page, click **Start New Project**, upload a phone video or photos, and watch the AI generate the 3D model and explainer video!
