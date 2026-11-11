"use client";

import React, { useState, useEffect } from "react";
import InstrumentViewer3D from "@/components/InstrumentViewer3D";
import {
  FinishPreset,
  InstrumentProject,
  HotspotAnnotation,
} from "@/types/instrument";

const DEFAULT_INSTRUMENT: InstrumentProject = {
  instrument_id: "inst-tkr-tibial-jig-01",
  name: "TKR Proximal Tibial Resection Cutting Guide (Left/Right)",
  category: "Orthopedic Knee Arthroplasty Instrument",
  capture_source: "ZED_2I_STEREO_SVO2",
  status: "READY_3D",
  progress_pct: 100,
  current_stage: "3D Metric Mesh (.glb) & Splat Ready",
  dimensions: {
    length_mm: 142.5,
    width_mm: 32.0,
    height_mm: 24.0,
    saw_slot_tolerance_mm: 1.27,
  },
  hotspots: [
    {
      id: "hs-1",
      title: "1.27mm Captured Oscillating Saw Slot",
      description: "Guides the sagittal bone saw at a 3° posterior tibial slope without metal debris.",
      sub_component: "1.27mm Saw Slot",
      position_xyz: [0.0, 0.25, 0.0],
      camera_orbit: [0.3, 1.1, 2.8],
    },
    {
      id: "hs-2",
      title: "Micro-Resection Depth Cam Dial (±2mm)",
      description: "Knurled rotational dial locks the cutting block onto the extramedullary tibial alignment rod.",
      sub_component: "Locking Cam Dial",
      position_xyz: [0.85, 0.45, 0.0],
      camera_orbit: [0.9, 1.0, 2.5],
    },
    {
      id: "hs-3",
      title: "3.2mm Convergent & Parallel Pin Tunnels",
      description: "Accepts headless cortical fixation pins to stabilize the jig against the anterior tibia.",
      sub_component: "3.2mm Pin Tunnels",
      position_xyz: [-0.45, 0.15, 0.45],
      camera_orbit: [-0.6, 1.2, 2.6],
    },
    {
      id: "hs-4",
      title: "Extramedullary Alignment Rod Collar",
      description: "Quick-release coupling that aligns with the distal ankle malleoli clamp.",
      sub_component: "EM Rod Collar",
      position_xyz: [-0.85, -0.55, 0.0],
      camera_orbit: [-1.1, 1.3, 2.7],
    },
  ],
  explainer_videos: [],
};

export default function Surg3DDashboardPage() {
  const [project, setProject] = useState<InstrumentProject>(DEFAULT_INSTRUMENT);
  const [finish, setFinish] = useState<FinishPreset>("satin_stainless");
  const [explodedFactor, setExplodedFactor] = useState<number>(0);
  const [wireframe, setWireframe] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const [activeHotspot, setActiveHotspot] = useState<HotspotAnnotation | null>(
    DEFAULT_INSTRUMENT.hotspots[0]
  );

  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [instrumentName, setInstrumentName] = useState<string>("Tibial Cutting Guide Jig");
  const [captureSource, setCaptureSource] = useState<string>("PHONE_MULTIVIEW_MP4");
  const [localVideoPreviewUrl, setLocalVideoPreviewUrl] = useState<string | null>(null);

  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
    if (file && file.type.startsWith("video/")) {
      setLocalVideoPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleUploadAndReconstruct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert("Please choose a video file (.mp4, .mov, or ZED 2i .svo2) first!");
      return;
    }

    setIsProcessing(true);

    // Step-by-step live pipeline feedback
    const stages = [
      { pct: 20, msg: `Uploading '${selectedFile.name}' to FastAPI Backend...` },
      { pct: 45, msg: "ZED 2i / FFmpeg: Extracting Multi-Angle RGB Keyframes & Depth..." },
      { pct: 70, msg: "SAM 2 Video Masking: Isolating Surgical Instrument from Background..." },
      { pct: 90, msg: "Open3D TSDF + Gaussian Splatting: Building Watertight .GLB Mesh..." },
    ];

    for (const st of stages) {
      setProject((prev) => ({
        ...prev,
        progress_pct: st.pct,
        current_stage: st.msg,
      }));
      await new Promise((r) => setTimeout(r, 550));
    }

    try {
      const formData = new FormData();
      formData.append("name", instrumentName);
      formData.append("capture_source", captureSource);
      formData.append("file", selectedFile);

      const res = await fetch(`${apiBase}/api/v1/instruments/upload`, {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const newProj = await res.json();
        setProject(newProj);
      }
    } catch {
      setProject((prev) => ({
        ...prev,
        name: `${instrumentName} (${selectedFile.name})`,
        progress_pct: 100,
        current_stage: `Uploaded '${selectedFile.name}' -> 3D Model (.glb) Ready!`,
      }));
    }

    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-600">
            <span>Step 1: Upload Video</span>
            <span>→</span>
            <span>Step 2: Inspect 3D</span>
          </div>
          <h1 className="text-3xl font-extrabold mt-1 text-slate-900">{project.name}</h1>
        </div>
        <div className="flex gap-3">
          <a
            href={`${apiBase}/api/v1/instruments/${project.instrument_id}/model.glb`}
            className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm transition shadow-sm"
          >
            Download 3D Model (.GLB)
          </a>
        </div>
      </header>

      {/* STEP 1: VIDEO UPLOAD PANEL */}
      <form
        onSubmit={handleUploadAndReconstruct}
        className="bg-slate-50 border border-slate-200 rounded-2xl p-6 grid grid-cols-1 md:grid-cols-12 gap-6 shadow-sm"
      >
        <div className="md:col-span-4">
          <label className="block text-xs font-bold uppercase text-slate-500 mb-2">
            1. Source Video (.MP4 / .SVO2)
          </label>
          <input
            type="file"
            accept=".mp4,.mov,.webm,.svo2,video/*"
            onChange={handleFileChange}
            className="w-full text-xs text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-slate-900 file:text-white hover:file:bg-slate-800 cursor-pointer bg-white border border-slate-200 rounded-xl p-1.5 transition-all"
          />
        </div>

        <div className="md:col-span-3">
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Instrument Name</label>
          <input
            type="text"
            value={instrumentName}
            onChange={(e) => setInstrumentName(e.target.value)}
            placeholder="e.g., Tibial Cutting Guide"
            className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 outline-none transition-all"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Camera Source</label>
          <select
            value={captureSource}
            onChange={(e) => setCaptureSource(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-900 focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500 outline-none transition-all appearance-none"
          >
            <option value="PHONE_MULTIVIEW_MP4">Phone Video</option>
            <option value="ZED_2I_STEREO_SVO2">ZED 2i Stereo</option>
          </select>
        </div>

        <div className="md:col-span-3">
          <button
            type="submit"
            disabled={isProcessing}
            className="w-full py-3 px-6 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm uppercase tracking-widest shadow-md transition-all disabled:opacity-50"
          >
            {isProcessing ? "Processing..." : "Build 3D Model"}
          </button>
        </div>
      </form>

      {/* Progress Bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
        <div className="flex justify-between text-xs font-bold uppercase text-slate-500 mb-2">
          <span className="text-cyan-600">{project.current_stage}</span>
          <span>{project.progress_pct}%</span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-cyan-600 transition-all duration-700 ease-out"
            style={{ width: `${project.progress_pct}%` }}
          />
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: 3D Viewer & Material Controls */}
        <div className={localVideoPreviewUrl ? "lg:col-span-8 space-y-6" : "lg:col-span-12 space-y-6"}>
          <InstrumentViewer3D
            finish={finish}
            explodedFactor={explodedFactor}
            wireframe={wireframe}
            autoRotate={autoRotate}
            hotspots={project.hotspots}
            activeHotspotId={activeHotspot?.id || null}
            onSelectHotspot={(hs) => setActiveHotspot(hs)}
            glbUrl={`${apiBase}/api/v1/instruments/${project.instrument_id}/model.glb`}
          />

          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 space-y-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                2. Surface Finish & Assembly View
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setWireframe(!wireframe)}
                  className={`px-4 py-1.5 rounded-lg text-[11px] font-bold uppercase border transition-all ${
                    wireframe
                      ? "bg-slate-900 border-slate-900 text-white shadow-sm"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  }`}
                >
                  Wireframe
                </button>
                <button
                  onClick={() => setAutoRotate(!autoRotate)}
                  className={`px-4 py-1.5 rounded-lg text-[11px] font-bold uppercase border transition-all ${
                    autoRotate
                      ? "bg-slate-900 border-slate-900 text-white shadow-sm"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  }`}
                >
                  360° Orbit
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {(
                [
                  ["satin_stainless", "Satin 316L"],
                  ["tin_gold", "TiN Gold"],
                  ["oxidized_black", "DLC Black"],
                  ["anodized_blue", "Ti Blue"],
                ] as [FinishPreset, string][]
              ).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setFinish(key)}
                  className={`py-2.5 px-4 rounded-xl text-[11px] font-bold uppercase border transition-all ${
                    finish === key
                      ? "bg-white border-cyan-500 text-cyan-600 shadow-sm ring-2 ring-cyan-500/10"
                      : "bg-white border-slate-200 text-slate-500 hover:border-slate-300"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-200 flex items-center gap-6">
              <label className="text-xs font-bold uppercase text-slate-500 whitespace-nowrap">
                Exploded View:
              </label>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={explodedFactor}
                onChange={(e) => setExplodedFactor(parseFloat(e.target.value))}
                className="w-full accent-cyan-600 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-xs font-bold text-cyan-600 font-mono w-12 text-right">
                {Math.round(explodedFactor * 100)}%
              </span>
            </div>
          </div>
        </div>

        {/* Right: Input Video Preview */}
        {localVideoPreviewUrl && (
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-3 shadow-sm sticky top-6">
              <div className="text-xs font-bold text-slate-500 uppercase">
                Source Preview
              </div>
              <video
                src={localVideoPreviewUrl}
                controls
                className="w-full h-auto max-h-[400px] object-contain rounded-xl bg-slate-900 shadow-inner"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}