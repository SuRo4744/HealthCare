"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createProject, uploadFiles, start3DReconstruction } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [projectName, setProjectName] = useState("");
  const [productType, setProductType] = useState("Surgical Implant");
  const [description, setDescription] = useState("");
  const [fileType, setFileType] = useState("video");
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName.trim()) {
      setError("Please enter a project name");
      return;
    }
    if (!files || files.length === 0) {
      setError("Please select at least one file");
      return;
    }

    try {
      setLoading(true);
      setError("");

      // 1. Create project
      const project = await createProject({
        name: projectName,
        product_type: productType,
        description: description,
      });

      const projectId = project.id;

      // 2. Upload files
      await uploadFiles(projectId, files, fileType);

      // 3. Start 3D Reconstruction
      await start3DReconstruction(projectId);

      // 4. Redirect to project status / viewer page
      router.push(`/projects/${projectId}`);
    } catch (err: any) {
      setError(err.message || "Failed to process upload");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white">
      <div className="max-w-3xl mx-auto px-6 py-16">
        <Link href="/" className="text-sm text-slate-600 dark:text-slate-400 hover:underline mb-8 inline-block">
          ← Back to home
        </Link>

        <h1 className="text-3xl font-bold mb-2">
          New Healthcare Visualization Project
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mb-8">
          Upload phone videos or photos. Our AI pipeline reconstructs a 3D model and generates an explainer video.
        </p>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-950/50 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Product Name</label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g. Titanium Spinal Implant"
                className="w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Product Type</label>
              <select
                value={productType}
                onChange={(e) => setProductType(e.target.value)}
                className="w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="Surgical Implant">Surgical Implant</option>
                <option value="Surgical Instrument">Surgical Instrument</option>
                <option value="Diagnostic Device">Diagnostic Device</option>
                <option value="Orthopedic Hardware">Orthopedic Hardware</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description / Notes</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Details for surgeons, sales reps, or patients..."
                className="w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                rows={3}
              />
            </div>
          </div>

          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <div className="flex gap-4 mb-4">
              <button
                type="button"
                onClick={() => setFileType("video")}
                className={`flex-1 py-2 px-4 rounded-xl text-sm font-medium border transition-colors ${
                  fileType === "video"
                    ? "bg-blue-600 text-white border-blue-600"
                    : "border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400"
                }`}
              >
                🎥 Video Upload (Recommended)
              </button>
              <button
                type="button"
                onClick={() => setFileType("photo")}
                className={`flex-1 py-2 px-4 rounded-xl text-sm font-medium border transition-colors ${
                  fileType === "photo"
                    ? "bg-blue-600 text-white border-blue-600"
                    : "border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400"
                }`}
              >
                📸 Multiple Photos
              </button>
            </div>

            <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-8 text-center">
              <input
                type="file"
                multiple={fileType === "photo"}
                accept={fileType === "video" ? "video/*" : "image/*"}
                onChange={(e) => setFiles(e.target.files)}
                className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 dark:file:bg-blue-950 dark:file:text-blue-300 hover:file:bg-blue-100"
              />
              <p className="text-xs text-slate-500 mt-2">
                {files && files.length > 0 ? `${files.length} file(s) selected` : "No files selected"}
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl transition-colors shadow-lg shadow-blue-600/20 disabled:opacity-50"
          >
            {loading ? "Processing 3D Reconstruction..." : "Generate 3D Model & Explainer Video"}
          </button>
        </form>
      </div>
    </main>
  );
}
