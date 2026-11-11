# Frontend - Video to 3D Model to Explainer Video

Next.js frontend for healthcare product visualization platform.

## Features
- Upload videos/photos for 3D reconstruction
- Monitor processing pipeline
- View 3D models
- Generate explainer videos
- Multi-language support
- Audience targeting

## Tech Stack
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- React Three Fiber (3D viewer)
- Axios for API calls

## Development

```bash
npm install
npm run dev
```

Runs on http://localhost:3000

## Environment
Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure
```
app/
  page.tsx          # Landing page
  upload/           # Upload media
  projects/         # Project list
  projects/[id]/    # Project detail
  viewer/           # 3D model viewer
components/
  UploadDropzone/
  ProjectCard/
  VideoPlayer/
  ModelViewer/
