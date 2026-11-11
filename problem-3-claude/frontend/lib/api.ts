export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createProject(data: {
  name: string;
  description?: string;
  product_type?: string;
  target_audience?: string;
  language?: string;
}) {
  const res = await fetch(`${API_BASE_URL}/api/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

export async function uploadFiles(projectId: string, files: FileList | File[], fileType: string = "photo") {
  const formData = new FormData();
  formData.append("project_id", projectId);
  formData.append("file_type", fileType);

  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  const res = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload files");
  return res.json();
}

export async function start3DReconstruction(projectId: string) {
  const formData = new FormData();
  formData.append("project_id", projectId);

  const res = await fetch(`${API_BASE_URL}/api/process/3d-model`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to start 3D reconstruction");
  return res.json();
}

export async function generateExplainerVideo(data: {
  project_id: string;
  product_name: string;
  product_type: string;
  language?: string;
}) {
  const res = await fetch(`${API_BASE_URL}/api/generate/explainer-video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to generate explainer video");
  return res.json();
}

export async function getProjectStatus(projectId: string) {
  const res = await fetch(`${API_BASE_URL}/api/projects/${projectId}/status`);
  if (!res.ok) throw new Error("Failed to fetch project status");
  return res.json();
}
