"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ModelViewer from "@/components/ModelViewer";
import { API_BASE_URL } from "@/lib/api";

export default function ProjectDetail({ params }: { params: Promise<{ id: string }> }) {
  const [projectId, setProjectId] = useState<string>("");
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [videoResult, setVideoResult] = useState<any>(null);
  const [fetchError, setFetchError] = useState<string>("");

  // Resolve params promise safely
  useEffect(() => {
    params.then((p) => setProjectId(p.id));
  }, [params]);

  const fetchStatus = async () => {
    if (!projectId) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/projects/${projectId}/status`, {
        // Short timeout so a transient hiccup doesn't strand the UI
        signal: AbortSignal.timeout(8000),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setProject(data);
      setFetchError("");
      setLoading(false);

      // If a video was started but not yet finished, keep polling for the
      // actual result instead of leaving video_path empty forever.
      if (data?.artifacts?.explainer_video) {
        try {
          const vres = await fetch(
            `${API_BASE_URL}/api/projects/${projectId}/video`
          );
          if (vres.ok) {
            setVideoResult(await vres.json());
          }
        } catch {
          // Non-fatal — the status poll will retry
        }
      }
    } catch (err: any) {
      // Don't abandon the UI on a transient failure. Keep showing the last
      // known state and keep polling; only surface an error if it persists.
      console.error("fetchStatus failed:", err);
      setFetchError("Connection to backend lost — retrying...");
      if (!project) setLoading(false);
    }
  };

  useEffect(() => {
    if (!projectId) return;
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [projectId]);

  const handleGenerateVideo = async () => {
    try {
      setGeneratingVideo(true);
      setFetchError("");
      const res = await fetch(`${API_BASE_URL}/api/generate/explainer-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          product_name: project?.name || "Medical Device",
          product_type: project?.product_type || "Surgical Implant",
          language: "en",
        }),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setVideoResult(data);
    } catch (err: any) {
      console.error(err);
      setFetchError("Failed to start video generation");
    } finally {
      setGeneratingVideo(false);
    }
  };

  if (loading || !projectId) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="animate-pulse text-lg">Loading project...</div>
      </div>
    );
  }

  const modelPath = project?.artifacts?.model_3d;
  // The backend stores paths relative to the backend CWD; expose via the
  // dedicated model endpoint so the frontend never has to guess the path.
  const modelUrl = modelPath
    ? `${API_BASE_URL}/api/projects/${projectId}/model?format=obj`
    : undefined;

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <Link href="/upload" className="text-sm text-slate-600 dark:text-slate-400 hover:underline mb-8 inline-block">
          ← Upload another
        </Link>

        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">{project?.name || "Project Details"}</h1>
            <p className="text-slate-600 dark:text-slate-400">
              Status: <span className="font-semibold uppercase text-blue-500">{project?.status}</span> • Progress: {project?.progress}%
            </p>
            {fetchError && (
              <p className="text-sm text-amber-400 mt-1">{fetchError}</p>
            )}
          </div>
          <button
            onClick={handleGenerateVideo}
            disabled={generatingVideo}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors shadow-lg disabled:opacity-50"
          >
            {generatingVideo ? "Generating Video..." : "🎬 Generate Explainer Video"}
          </button>
        </div>

        {/* Progress steps */}
        <div className="grid md:grid-cols-3 gap-4 mb-12">
          {project?.steps?.map((step: any, i: number) => (
            <div key={i} className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Step {i + 1}</div>
              <div className="font-medium mb-1">{step.description}</div>
              <div className="text-sm text-blue-500 capitalize">{step.status}</div>
            </div>
          ))}
        </div>

        {/* 3D Model Viewer */}
        <div className="mb-12">
          <h2 className="text-xl font-bold mb-4">Interactive 3D Model Preview</h2>
          <ModelViewer modelUrl={modelUrl} />
        </div>

        {/* Video result section */}
        {videoResult && (
          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
            <h2 className="text-xl font-bold mb-4">Generated Explainer Video</h2>
            {videoResult.video_path ? (
              <div className="space-y-3">
                <video
                  controls
                  className="w-full rounded-xl bg-black"
                  src={`${API_BASE_URL}/api/projects/${projectId}/video`}
                />
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Duration: {videoResult.duration}s • Status: {videoResult.status}
                </p>
              </div>
            ) : (
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                Status: {videoResult.status} • Video path: Processing...
              </p>
            )}
            <div className="p-4 bg-slate-900 text-slate-300 rounded-xl font-mono text-sm">
              {JSON.stringify(videoResult, null, 2)}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}