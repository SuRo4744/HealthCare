import os
import json
import struct
import numpy as np

def make_box(center, extents, rot_z_deg=0.0):
    cx, cy, cz = center
    lx, ly, lz = extents[0] / 2.0, extents[1] / 2.0, extents[2] / 2.0
    v = np.array([
        [-lx, -ly,  lz], [ lx, -ly,  lz], [ lx,  ly,  lz], [-lx,  ly,  lz],
        [-lx, -ly, -lz], [ lx, -ly, -lz], [ lx,  ly, -lz], [-lx,  ly, -lz],
    ], dtype=np.float32)
    if rot_z_deg != 0.0:
        rad = np.radians(rot_z_deg)
        c, s = np.cos(rad), np.sin(rad)
        rot = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)
        v = v @ rot.T
    v += np.array([cx, cy, cz], dtype=np.float32)
    idx = np.array([
        0,1,2, 2,3,0,  1,5,6, 6,2,1,  5,4,7, 7,6,5,
        4,0,3, 3,7,4,  3,2,6, 6,7,3,  4,5,1, 1,0,4
    ], dtype=np.uint16)
    return v, idx

def make_cylinder(center, radius, height, axis="y", sections=32):
    cx, cy, cz = center
    angles = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    half_h = height / 2.0
    verts = []
    # Top and bottom rings
    for y_val in [-half_h, half_h]:
        for a in angles:
            px, pz = radius * np.cos(a), radius * np.sin(a)
            if axis == "y":
                verts.append([cx + px, cy + y_val, cz + pz])
            elif axis == "x":
                verts.append([cx + y_val, cy + px, cz + pz])
            else:
                verts.append([cx + px, cy + pz, cz + y_val])
    # Center caps
    if axis == "y":
        verts.append([cx, cy - half_h, cz])
        verts.append([cx, cy + half_h, cz])
    elif axis == "x":
        verts.append([cx - half_h, cy, cz])
        verts.append([cx + half_h, cy, cz])
    else:
        verts.append([cx, cy, cz - half_h])
        verts.append([cx, cy, cz + half_h])

    v = np.array(verts, dtype=np.float32)
    bot_center = 2 * sections
    top_center = 2 * sections + 1
    tris = []
    for i in range(sections):
        nxt = (i + 1) % sections
        # Side quad
        b0, b1 = i, nxt
        t0, t1 = i + sections, nxt + sections
        tris.extend([b0, b1, t1, t1, t0, b0])
        # Caps
        tris.extend([bot_center, b1, b0])
        tris.extend([top_center, t0, t1])
    return v, np.array(tris, dtype=np.uint16)

def generate_procedural_tibial_cutting_guide_glb(output_glb_path: str) -> str:
    """
    Generates a high-detail 3D .glb model of the Handheld Robotic Surgical Saw
    from 00:18-00:23 of the Scopic Vision knee replacement video.
    """
    os.makedirs(os.path.dirname(output_glb_path), exist_ok=True)

    parts = [
        # 1. Angled Ergonomic Pistol Grip
        make_box(center=[-0.065, -0.042, 0.0], extents=[0.028, 0.095, 0.026], rot_z_deg=-16.0),
        # 2. Rear Thumb Support Strut (Seen at 00:18-00:20)
        make_box(center=[-0.102, -0.005, 0.0], extents=[0.014, 0.075, 0.022], rot_z_deg=22.0),
        # 3. Horizontal Upper Trigger & Actuator Body
        make_box(center=[-0.045, 0.018, 0.0], extents=[0.095, 0.032, 0.032], rot_z_deg=-4.0),
        # 4. Horizontal Cylindrical Drive Barrel
        make_cylinder(center=[-0.005, 0.015, 0.0], radius=0.018, height=0.055, axis="x", sections=36),
        # 5. Main Vertical Chrome Rotary Motor Head (Center cylinder at 00:19-00:22)
        make_cylinder(center=[0.032, 0.012, 0.0], radius=0.021, height=0.068, axis="y", sections=48),
        # 6. Top Motor Cap Ring
        make_cylinder(center=[0.032, 0.048, 0.0], radius=0.017, height=0.008, axis="y", sections=36),
        # 7. Lower Blade Collet & Clamp Block
        make_box(center=[0.035, -0.028, 0.0], extents=[0.038, 0.026, 0.030]),
        # 8. Long Extending Sagittal Bone Saw Guide Bar (00:18-00:23)
        make_box(center=[0.125, -0.032, 0.0], extents=[0.155, 0.009, 0.016]),
        # 9. Guide Pin Bosses on the Saw Blade
        make_cylinder(center=[0.115, -0.032, 0.0], radius=0.0035, height=0.020, axis="z", sections=20),
        make_cylinder(center=[0.165, -0.032, 0.0], radius=0.0035, height=0.020, axis="z", sections=20),
    ]

    all_verts = []
    all_indices = []
    offset = 0
    for v, idx in parts:
        all_verts.append(v)
        all_indices.append(idx + offset)
        offset += len(v)

    vertices = np.vstack(all_verts).astype(np.float32)
    indices = np.concatenate(all_indices).astype(np.uint16)

    # Compute normals
    normals = np.zeros_like(vertices)
    for i in range(0, len(indices), 3):
        i0, i1, i2 = indices[i], indices[i+1], indices[i+2]
        v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
        n = np.cross(v1 - v0, v2 - v0)
        normals[i0] += n
        normals[i1] += n
        normals[i2] += n
    normals /= np.linalg.norm(normals, axis=1, keepdims=True)
    normal_bytes = normals.astype(np.float32).tobytes()

    vertex_bytes = vertices.tobytes()
    index_bytes = indices.tobytes()

    # Buffer: Vertices + Normals + Indices
    bin_chunk = vertex_bytes + normal_bytes + index_bytes
    while len(bin_chunk) % 4 != 0:
        bin_chunk += b"\x00"

    gltf_dict = {
        "asset": {"version": "2.0", "generator": "SURG-3D High-Detail Robotic Saw Pipeline"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "Robotic_Handheld_Surgical_Saw_00_18_HighDetail"}],
        "meshes": [{
            "name": "Robotic_Saw_Handpiece_HighDetail",
            "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "material": 0}]
        }],
        "materials": [{
            "name": "Surgical_316L_Chrome_Alloy",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.88, 0.91, 0.95, 1.0],
                "metallicFactor": 0.90,
                "roughnessFactor": 0.18
            }
        }],
        "buffers": [{"byteLength": len(bin_chunk)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(vertex_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": len(vertex_bytes), "byteLength": len(normal_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": len(vertex_bytes) + len(normal_bytes), "byteLength": len(index_bytes), "target": 34963}
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": len(vertices),
                "type": "VEC3",
                "max": vertices.max(axis=0).tolist(),
                "min": vertices.min(axis=0).tolist()
            },
            {
                "bufferView": 1,
                "componentType": 5126,
                "count": len(normals),
                "type": "VEC3"
            },
            {
                "bufferView": 2,
                "componentType": 5123,
                "count": len(indices),
                "type": "SCALAR",
                "max": [int(indices.max())],
                "min": [int(indices.min())]
            }
        ]
    }

    json_bytes = json.dumps(gltf_dict, separators=(",", ":")).encode("utf-8")
    while len(json_bytes) % 4 != 0:
        json_bytes += b" "

    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_chunk)
    header = struct.pack("<4sII", b"glTF", 2, total_length)
    json_header = struct.pack("<I4s", len(json_bytes), b"JSON")
    bin_header = struct.pack("<I4s", len(bin_chunk), b"BIN\x00")

    with open(output_glb_path, "wb") as f:
        f.write(header + json_header + json_bytes + bin_header + bin_chunk)

    return output_glb_path
