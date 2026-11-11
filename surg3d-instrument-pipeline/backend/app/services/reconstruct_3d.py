import os
import json
import struct
import numpy as np
import subprocess
import shutil
import sqlite3
from typing import Dict, Any

try:
    import open3d as o3d
except ImportError:
    o3d = None

try:
    from PIL import Image
except ImportError:
    Image = None

def extract_frames_from_video(video_path: str, output_dir: str):
    """Uses ffmpeg to extract frames from the uploaded video."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Extract 2 frames per second for better reconstruction density
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", "fps=2",
        os.path.join(output_dir, "frame_%04d.jpg")
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Frames extracted to {output_dir}")

def run_colmap_sfm(frames_dir: str, output_dir: str):
    """
    Runs a simplified COLMAP SfM pipeline:
    Feature extraction -> Matching -> Mapper
    """
    colmap_bin = shutil.which("colmap")
    if not colmap_bin:
        print("COLMAP not found in PATH. Skipping SfM.")
        return False

    database_path = os.path.join(output_dir, "database.db")
    sparse_path = os.path.join(output_dir, "sparse")
    os.makedirs(sparse_path, exist_ok=True)

    try:
        # 1. Feature extraction
        subprocess.run([
            colmap_bin, "feature_extractor",
            "--database_path", database_path,
            "--image_path", frames_dir,
            "--ImageReader.single_camera", "1"
        ], check=True, stdout=subprocess.DEVNULL)

        # 2. Matching (Exhaustive for small datasets)
        subprocess.run([
            colmap_bin, "exhaustive_matcher",
            "--database_path", database_path
        ], check=True, stdout=subprocess.DEVNULL)

        # 3. Mapping
        subprocess.run([
            colmap_bin, "mapper",
            "--database_path", database_path,
            "--image_path", frames_dir,
            "--output_path", sparse_path
        ], check=True, stdout=subprocess.DEVNULL)

        return True
    except Exception as e:
        print(f"COLMAP SfM failed: {e}")
        return False

def save_as_valid_glb(mesh: o3d.geometry.TriangleMesh, output_glb_path: str):
    """
    Manually exports Open3D mesh to GLB to avoid Open3D exporter alignment bugs.
    """
    mesh.compute_vertex_normals()
    mesh.normalize_normals()

    verts = np.asarray(mesh.vertices).astype(np.float32)
    norms = np.asarray(mesh.vertex_normals).astype(np.float32)
    tris = np.asarray(mesh.triangles).astype(np.uint32)

    v_bytes = verts.tobytes()
    n_bytes = norms.tobytes()
    i_bytes = tris.tobytes()

    def pad(b):
        while len(b) % 4 != 0:
            b += b"\x00"
        return b

    v_chunk = pad(v_bytes)
    n_chunk = pad(n_bytes)
    i_chunk = pad(i_bytes)

    # Offset tracking (must be 4-byte aligned)
    v_off = 0
    n_off = len(v_chunk)
    i_off = n_off + len(n_chunk)

    bin_chunk = v_chunk + n_chunk + i_chunk

    gltf_dict = {
        "asset": {"version": "2.0", "generator": "SURG-3D-Validated-Pipeline"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{
            "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "material": 0}]
        }],
        "materials": [{"pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.8, 0.8, 1.0], "metallicFactor": 0.5}}],
        "buffers": [{"byteLength": len(bin_chunk)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": v_off, "byteLength": len(v_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": n_off, "byteLength": len(n_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": i_off, "byteLength": len(i_bytes), "target": 34963}
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(verts), "type": "VEC3",
             "max": verts.max(axis=0).tolist(), "min": verts.min(axis=0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(norms), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5125, "count": len(tris) * 3, "type": "SCALAR",
             "max": [int(tris.max())], "min": [int(tris.min())]}
        ]
    }

    json_bytes = json.dumps(gltf_dict, separators=(",", ":")).encode("utf-8")
    json_bytes = pad(json_bytes)

    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_chunk)
    header = struct.pack("<4sII", b"glTF", 2, total_length)
    json_chunk = struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes
    bin_chunk_data = struct.pack("<I4s", len(bin_chunk), b"BIN\x00") + bin_chunk

    with open(output_glb_path, "wb") as f:
        f.write(header + json_chunk + bin_chunk_data)

def generate_mesh_from_sfm(sparse_path: str, work_dir: str, output_glb_path: str):
    if not o3d:
        print("Open3D not installed. Cannot generate real mesh.")
        return False

    recon_base = os.path.join(sparse_path, "0")
    if not os.path.exists(recon_base):
        return False

    try:
        ply_path = os.path.join(work_dir, "points.ply")
        colmap_bin = shutil.which("colmap")
        if not colmap_bin:
            return False

        subprocess.run([
            colmap_bin, "model_converter",
            "--input_path", recon_base,
            "--output_path", ply_path,
            "--output_type", "PLY"
        ], check=True, stdout=subprocess.DEVNULL)

        if not os.path.exists(ply_path):
            return False

        pcd = o3d.io.read_point_cloud(ply_path)
        if pcd.is_empty():
            print("Exported PLY is empty.")
            return False

        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        pcd.orient_normals_consistent_tangent_plane(k=10)

        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)

        vertices_to_remove = densities < np.quantile(densities, 0.05)
        mesh.remove_vertices_by_mask(vertices_to_remove)

        save_as_valid_glb(mesh, output_glb_path)
        print(f"Successfully reconstructed 3D mesh GLB -> {output_glb_path}")
        return True

    except Exception as e:
        print(f"Mesh generation failed: {e}")
        return False

def run_instrument_3d_reconstruction(instrument_id: str, storage_dir: str) -> Dict[str, Any]:
    input_video_path = os.path.join(storage_dir, "uploads", f"{instrument_id}_input.mp4")
    work_dir = os.path.join(storage_dir, "work", instrument_id)
    frames_dir = os.path.join(storage_dir, "frames", instrument_id)
    glb_path = os.path.join(storage_dir, f"{instrument_id}_reconstructed.glb")

    os.makedirs(work_dir, exist_ok=True)

    if os.path.exists(input_video_path):
        extract_frames_from_video(input_video_path, frames_dir)
    else:
        return {"error": "Input video not found"}

    sfm_success = run_colmap_sfm(frames_dir, work_dir)

    mesh_success = False
    if sfm_success:
        mesh_success = generate_mesh_from_sfm(os.path.join(work_dir, "sparse"), work_dir, glb_path)

    if not mesh_success:
        print("Reconstruction failed or tools missing. Falling back to procedural model.")
        from app.services.reconstruct_3d_procedural import generate_procedural_tibial_cutting_guide_glb
        generate_procedural_tibial_cutting_guide_glb(glb_path)
        status = "FALLBACK_PROCEDURAL"
    else:
        status = "REAL_RECONSTRUCTION"

    return {
        "mesh_glb_path": glb_path,
        "status": status,
        "frames_extracted_path": frames_dir
    }
