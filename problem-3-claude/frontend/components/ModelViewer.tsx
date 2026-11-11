"use client";

import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useRef, Suspense, useState, useEffect } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader.js";

function PlaceholderMesh() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.5;
    }
  });

  return (
    <mesh ref={meshRef}>
      <torusKnotGeometry args={[1, 0.3, 128, 32]} />
      <meshStandardMaterial color="#3b82f6" metalness={0.8} roughness={0.2} />
    </mesh>
  );
}

function ObjMesh({ url }: { url: string }) {
  const obj = useLoader(OBJLoader, url);
  const meshRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.5;
    }
  });

  // Center and normalize the loaded model so it fits nicely in view
  const box = new THREE.Box3().setFromObject(obj);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z, 0.0001);
  const scale = 2.5 / maxDim;

  return (
    <group ref={meshRef} scale={scale} position={[0, 0, 0]}>
      <primitive object={obj} />
    </group>
  );
}

export default function ModelViewer({ modelUrl }: { modelUrl?: string }) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Defer to next tick so the loader has the URL settled
    const id = requestAnimationFrame(() => setReady(true));
    return () => cancelAnimationFrame(id);
  }, [modelUrl]);

  const hasModel = !!modelUrl && ready;

  return (
    <div className="w-full h-[400px] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 relative">
      <div className="absolute top-4 left-4 z-10 px-3 py-1 rounded bg-slate-900/80 text-white text-xs font-medium border border-slate-700">
        Interactive 3D Model (OBJ / GLB)
      </div>
      <Canvas camera={{ position: [0, 0, 4] }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />
        {hasModel ? (
          <Suspense fallback={<PlaceholderMesh />}>
            <ObjMesh url={modelUrl} />
          </Suspense>
        ) : (
          <PlaceholderMesh />
        )}
        <OrbitControls enableZoom={true} enablePan={true} />
      </Canvas>
    </div>
  );
}