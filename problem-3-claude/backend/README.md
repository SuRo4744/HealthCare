# Backend - Video to 3D Model Pipeline

FastAPI backend for healthcare product visualization platform.

## Features
- File upload (video/photos)
- 3D model generation pipeline
- Explainer video generation
- Project management
- Multi-language support

## Tech Stack
- FastAPI
- Python 3.9+
- Uvicorn
- Pillow for image processing

## Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app:app --reload --port 8000
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Service health
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `POST /api/upload` - Upload files
- `POST /api/process/3d-model` - Start 3D processing
- `GET /api/projects/{id}/status` - Project status

## Environment
Copy `.env.example` to `.env` and configure.

## Project Structure
```
backend/
  app.py              # Main FastAPI app
  requirements.txt    # Dependencies
  .env               # Environment variables
  uploads/           # Uploaded media
  outputs/           # Generated 3D models & videos
```
