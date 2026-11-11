"use client";

"use client";

import React, { useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Html, ContactShadows, Environment, useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { FinishPreset, HotspotAnnotation } from "@/types/instrument";

const FINISH_MATERIALS: Record<
  FinishPreset,
  { color: string; metalness: number; roughness: number; label: string }
> = {
  satin_stainless: {
    color: "#e2e8f0",
    metalness: 0.9,
    roughness: 0.2,
    label: "316L Stainless & Medical White Polymer",
  },
  tin_gold: {
    color: "#eab308",
    metalness: 0.95,
    roughness: 0.18,
    label: "TiN Gold Anti-Glare Coating",
  },
  oxidized_black: {
    color: "#27272a",
    metalness: 0.85,
    roughness: 0.28,
    label: "DLC Matte Black Finish",
  },
  anodized_blue: {
    color: "#38bdf8",
    metalness: 0.88,
    roughness: 0.25,
    label: "Anodized Titanium Blue",
  },
};

interface ViewerProps {
  finish: FinishPreset;
  explodedFactor: number;
  wireframe: boolean;
  autoRotate: boolean;
  hotspots: HotspotAnnotation[];
  activeHotspotId: string | null;
  onSelectHotspot: (hs: HotspotAnnotation) => void;
  glbUrl?: string;
}

interface ModelProps extends ViewerProps {
  hoveredPart: string | null;
  setHoveredPart: (part: string | null) => void;
}

function ProceduralModel({
  finish,
  explodedFactor,
  wireframe,
  autoRotate,
  hotspots,
  activeHotspotId,
  onSelectHotspot,
  setHoveredPart,
}: ModelProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [hoveredPinId, setHoveredPinId] = useState<string | null>(null);
  const matConfig = FINISH_MATERIALS[finish];

  useFrame((_, delta) => {
    if (autoRotate && groupRef.current) {
      groupRef.current.rotation.y += delta * 0.45;
    }
  });

  const bindHover = (partLabel: string) => ({
    onPointerOver: (e: any) => {
      e.stopPropagation();
      setHoveredPart(partLabel);
      document.body.style.cursor = "pointer";
    },
    onPointerOut: (e: any) => {
      e.stopPropagation();
      setHoveredPart(null);
      document.body.style.cursor = "auto";
    },
  });

  return (
    <group ref={groupRef}>
      {/* 1. Ergonomic Handheld Pistol Grip */}
      <mesh
        position={[-0.95 - explodedFactor * 0.4, -0.35 - explodedFactor * 0.3, 0]}
        rotation={[0, 0, -0.28]}
        castShadow
        {...bindHover("Ergonomic Pistol Grip Handle")}
      >
        <boxGeometry args={[0.38, 1.15, 0.34]} />
        <meshStandardMaterial
          color={finish === "satin_stainless" ? "#cbd5e1" : matConfig.color}
          metalness={0.35}
          roughness={0.4}
          wireframe={wireframe}
        />
      </mesh>

      {/* Rear Thumb Support Frame */}
      <mesh
        position={[-1.25 - explodedFactor * 0.5, 0.05, 0]}
        rotation={[0, 0, 0.35]}
        castShadow
        {...bindHover("Rear Thumb Support Strut")}
      >
        <boxGeometry args={[0.18, 0.85, 0.28]} />
        <meshStandardMaterial
          color={finish === "satin_stainless" ? "#cbd5e1" : matConfig.color}
          metalness={0.35}
          roughness={0.4}
          wireframe={wireframe}
        />
      </mesh>

      {/* 2. Upper Robotic Actuator Housing */}
      <mesh
        position={[-0.45, 0.28 + explodedFactor * 0.35, 0]}
        castShadow
        {...bindHover("Upper Trigger & Robotic Actuator Housing")}
      >
        <boxGeometry args={[1.15, 0.42, 0.42]} />
        <meshStandardMaterial
          color={finish === "satin_stainless" ? "#f1f5f9" : matConfig.color}
          metalness={0.5}
          roughness={0.3}
          wireframe={wireframe}
        />
      </mesh>

      {/* 3. Vertical Metallic Rotary Motor Head */}
      <mesh
        position={[0.25, 0.18 + explodedFactor * 0.45, 0]}
        castShadow
        {...bindHover("Rotary Motor Drive Head (Chrome Cylinder)")}
      >
        <cylinderGeometry args={[0.26, 0.26, 0.82, 32]} />
        <meshStandardMaterial
          color={matConfig.color}
          metalness={0.95}
          roughness={0.15}
          wireframe={wireframe}
        />
      </mesh>

      {/* 4. Lower Blade Clamp Block */}
      <mesh
        position={[0.28, -0.32 - explodedFactor * 0.25, 0]}
        castShadow
        {...bindHover("Distal Saw Blade Collet & Clamp Block")}
      >
        <boxGeometry args={[0.48, 0.32, 0.38]} />
        <meshStandardMaterial
          color={matConfig.color}
          metalness={0.92}
          roughness={0.2}
          wireframe={wireframe}
        />
      </mesh>

      {/* 5. Extending Sagittal Bone Saw Guide Bar */}
      <mesh
        position={[1.15 + explodedFactor * 0.75, -0.34, 0]}
        castShadow
        {...bindHover("1.27mm Oscillating Sagittal Bone Saw Blade")}
      >
        <boxGeometry args={[1.45, 0.1, 0.22]} />
        <meshStandardMaterial
          color={matConfig.color}
          metalness={0.96}
          roughness={0.14}
          wireframe={wireframe}
        />
      </mesh>

      {/* Calibration Pin Holes on the Saw Bar */}
      <mesh
        position={[1.05 + explodedFactor * 0.75, -0.34, 0.12]}
        {...bindHover("3.2mm Calibration Pin Hole (Proximal)")}
      >
        <sphereGeometry args={[0.03, 16, 16]} />
        <meshStandardMaterial color="#090d16" />
      </mesh>
      <mesh
        position={[1.55 + explodedFactor * 0.75, -0.34, 0.12]}
        {...bindHover("3.2mm Calibration Pin Hole (Distal)")}
      >
        <sphereGeometry args={[0.03, 16, 16]} />
        <meshStandardMaterial color="#090d16" />
      </mesh>

      {/* Hotspots */}
      {hotspots.map((hs, index) => {
        const isSelected = activeHotspotId === hs.id;
        const isHovered = hoveredPinId === hs.id;
        return (
          <Html key={hs.id} position={hs.position_xyz} center zIndexRange={[10, 0]}>
            <div
              className="relative flex items-center justify-center"
              onMouseEnter={() => {
                setHoveredPinId(hs.id);
                setHoveredPart(`${hs.sub_component}: ${hs.title}`);
              }}
              onMouseLeave={() => {
                setHoveredPinId(null);
                setHoveredPart(null);
              }}
            >
              <button
                type="button"
                onClick={() => onSelectHotspot(hs)}
                className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center transition-transform shadow-md border ${
                  isSelected || isHovered
                    ? "bg-cyan-600 text-white border-white scale-125"
                    : "bg-white text-cyan-600 border-cyan-600 hover:scale-110"
                }`}
              >
                {index + 1}
              </button>

              {isHovered && (
                <div className="absolute bottom-7 left-1/2 -translate-x-1/2 px-2.5 py-1 rounded-md bg-slate-950/95 text-cyan-300 border border-cyan-400/60 text-[11px] font-semibold whitespace-nowrap shadow-xl pointer-events-none">
                  {hs.sub_component}
                </div>
              )}
            </div>
          </Html>
        );
      })}
    </group>
  );
}

function GLBModel({
  finish,
  explodedFactor,
  wireframe,
  autoRotate,
  hotspots,
  activeHotspotId,
  onSelectHotspot,
  setHoveredPart,
  glbUrl,
}: ModelProps) {
  // Load the real GLB model from the backend
  const glb = useGLTF(glbUrl || "") as any;

  // Apply the selected finish to the model
  const matConfig = FINISH_MATERIALS[finish];

  useEffect(() => {
    if (glb.scene) {
      // Traverse the loaded model and apply finish material
      glb.scene.traverse((child: any) => {
        if (child.isMesh) {
          child.material = new THREE.MeshStandardMaterial({
            color: finish === "satin_stainless" ? "#cbd5e1" : matConfig.color,
            metalness: finish === "satin_stainless" ? 0.35 : matConfig.metalness,
            roughness: finish === "satin_stainless" ? 0.4 : matConfig.roughness,
            wireframe: wireframe,
          });
        }
      });
    }
  }, [finish, matConfig, wireframe, glb.scene]);

  useFrame((_, delta) => {
    if (autoRotate && glb.scene) {
      glb.scene.rotation.y += delta * 0.45;
      // Apply exploded factor by scaling along the X-axis
      glb.scene.scale.set(1 + explodedFactor * 0.1, 1 + explodedFactor * 0.1, 1 + explodedFactor * 0.1);
    }
  });

  const bindHover = (partLabel: string) => ({
    onPointerOver: (e: any) => {
      e.stopPropagation();
      setHoveredPart(partLabel);
      document.body.style.cursor = "pointer";
    },
    onPointerOut: (e: any) => {
      e.stopPropagation();
      setHoveredPart(null);
      document.body.style.cursor = "auto";
    },
  });

  return (
    <group ref={glb.scene} {...bindHover("Loaded Surgical Instrument Model")}>
      {/* Hotspots overlay for the loaded model */}
      {hotspots.map((hs, index) => {
        const isSelected = activeHotspotId === hs.id;
        return (
          <Html key={hs.id} position={hs.position_xyz} center zIndexRange={[10, 0]} distanceFactor={10}>
            <div
              className="relative flex items-center justify-center"
              onMouseEnter={() => setHoveredPart(`${hs.sub_component}: ${hs.title}`)}
              onMouseLeave={() => setHoveredPart(null)}
            >
              <button
                type="button"
                onClick={() => onSelectHotspot(hs)}
                className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center transition-transform shadow-md border ${
                  isSelected
                    ? "bg-cyan-600 text-white border-white scale-125"
                    : "bg-white text-cyan-600 border-cyan-600 hover:scale-110"
                }`}
              >
                {index + 1}
              </button>

              {isSelected && (
                <div className="absolute bottom-7 left-1/2 -translate-x-1/2 px-2.5 py-1 rounded-md bg-slate-950/95 text-cyan-300 border border-cyan-400/60 text-[11px] font-semibold whitespace-nowrap shadow-xl pointer-events-none">
                  {hs.sub_component}
                </div>
              )}
            </div>
          </Html>
        );
      })}
    </group>
  );
}

export default function InstrumentViewer3D(props: ViewerProps) {
  const [hoveredPart, setHoveredPart] = useState<string | null>(null);

  return (
    <div className="relative w-full h-[460px] rounded-2xl overflow-hidden bg-white border border-slate-200 shadow-sm">
      <Canvas shadows camera={{ position: [2.2, 1.2, 3.1], fov: 42 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 8, 5]} intensity={1.5} castShadow />
        <directionalLight position={[-5, -3, -4]} intensity={0.4} color="#0ea5e9" />
        <Environment preset="city" />

        {/* Always show ProceduralModel as fallback and conditional GLBModel */}
        {props.glbUrl && props.glbUrl.trim() !== "" ? (
          <GLBModel
            {...props}
            hoveredPart={hoveredPart}
            setHoveredPart={setHoveredPart}
          />
        ) : (
          <ProceduralModel
            {...props}
            hoveredPart={hoveredPart}
            setHoveredPart={setHoveredPart}
          />
        )}

        <ContactShadows position={[0, -1.25, 0]} opacity={0.2} scale={8} blur={2} />
        <OrbitControls makeDefault enableDamping dampingFactor={0.05} />
      </Canvas>

      {/* Top-Left Compact Info Pill */}
      <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-md border border-slate-200 rounded-xl px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest pointer-events-none shadow-sm">
        <span className="text-slate-900">3D Robotic Saw</span>
        <span className="mx-2 text-slate-300">|</span>
        <span>{FINISH_MATERIALS[props.finish].label}</span>
      </div>

      {/* Bottom-Center Live Mouse-Over Part Name Badge */}
      {hoveredPart ? (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-slate-900 text-white font-bold text-[11px] uppercase tracking-wider px-4 py-2 rounded-full shadow-lg pointer-events-none transition-all">
          🔍 {hoveredPart}
        </div>
      ) : (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 border border-slate-200 text-slate-400 text-[10px] font-bold uppercase tracking-widest px-4 py-2 rounded-full pointer-events-none shadow-sm">
          Hover to inspect parts
        </div>
      )}
    </div>
  );
}