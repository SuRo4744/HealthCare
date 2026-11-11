# Detailed Architecture: Surgical Instrument 3D Reconstruction & Explainer Pipeline

## Why Surgical Instruments Need a Specialized Pipeline
Orthopedic knee surgery instruments—such as a **Tibial Cutting Jig**, **Femoral Sizer**, **Intramedullary Alignment Rod**, or **Bone Rongeur Forceps**—pose two major computer vision challenges:
1. **High Specularity & Thin Geometry:** Surgical-grade 316L stainless steel and titanium reflect overhead operating room lights, causing standard photogrammetry (COLMAP) to fail or produce noisy holes.
2. **Cluttered Clinical Background:** During an operation or back-table setup, instruments sit on green surgical drapes or inside perforated sterilization trays alongside gloved hands.

### How Our Architecture Solves This
1. **ZED 2i Stereo Camera with Polarizer (`NEURAL_PLUS` Depth Mode):**
   Instead of guessing depth solely from RGB features, the ZED 2i uses a 120mm stereo baseline and a neural depth network trained to handle reflective surfaces, outputting metric-scale depth maps (`.png` 16-bit) and 6-DoF camera poses (`transforms.json`) directly from `.svo2` recordings.
2. **SAM 2 (Segment Anything Model 2) Video Masking:**
   Tracks only the target surgical instrument across all frames, zeroing out background pixels (drapes, hands, tray) in both the RGB and Depth maps prior to 3D fusion.
3. **Hybrid 3D Reconstruction (Open3D TSDF + 3D Gaussian Splatting):**
   - **Open3D TSDF (Truncated Signed Distance Function):** Integrates masked depth frames into a watertight, metric-accurate `.glb` polygon mesh in seconds.
   - **PBR Material Separation:** Applies configurable metallic/roughness shaders so users in Next.js can swap finishes (*Satin Stainless Steel*, *Titanium Nitride Gold*, *Matte PEEK Polymer*, *Anodized Aluminum*) in **0ms** without rescanning.
4. **Automated Explainer Video Generation (Stretch Goal):**
   - **Headless Blender (`bpy`)** loads the `.glb` instrument model, animates a 360-degree turntable and exploded sub-component separation along the Z-axis, renders 3D callout labels, and muxes AI voiceover audio generated for the chosen audience (*Scrub Nurse Training*, *Surgeon Sales Demo*, or *Patient Overview*) and language.

## Mermaid.js System Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as OR Trainer / Sales Rep
    participant ZED as ZED 2i / Phone Camera
    participant Next as Next.js 15 (R3F Studio)
    participant API as FastAPI Backend
    participant Worker as GPU Worker (SAM2 + Open3D + Blender)

    ZED->>Next: Capture .svo2 (Stereo RGB-D) or .mp4 Orbit Video
    Next->>API: POST /api/v1/instruments/upload (Metadata + File)
    API-->>Next: Returns instrument_id & WebSocket channel
    Next->>API: POST /api/v1/instruments/{id}/reconstruct
    API->>Worker: Enqueue reconstruct_instrument_task()
    Worker-->>Next: WS: [20%] Extracting ZED 2i Neural Depth & 6-DoF Poses
    Worker-->>Next: WS: [45%] SAM 2 Masking Instrument from OR Drape
    Worker-->>Next: WS: [75%] Open3D TSDF Fusion + Draco .glb Export
    Worker-->>Next: WS: [100%] Ready! Returns .glb URL & Metric Dimensions
    User->>Next: Rotates 3D Instrument, Toggles TiN Gold Finish, Pins Hotspots
    Next->>API: POST /api/v1/instruments/{id}/explainer (Audience, Language, Keyframes)
    API->>Worker: Enqueue generate_explainer_video_task()
    Worker-->>Next: WS: Rendering Headless Blender Turntable + Exploded View + TTS
    Worker-->>Next: Returns 1080p Explainer Video (.mp4) + Subtitles (.vtt)
```
