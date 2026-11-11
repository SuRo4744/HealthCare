export type FinishPreset =
  | "satin_stainless"
  | "tin_gold"
  | "oxidized_black"
  | "anodized_blue";

export type AudienceType = "scrub_nurse" | "surgeon" | "sales_rep" | "patient";
export type LanguageCode = "en-US" | "hi-IN" | "es-ES" | "de-DE";

export interface HotspotAnnotation {
  id: string;
  title: string;
  description: string;
  sub_component: string;
  position_xyz: [number, number, number];
  camera_orbit: [number, number, number];
}

export interface InstrumentDimensions {
  length_mm: number;
  width_mm: number;
  height_mm: number;
  saw_slot_tolerance_mm: number;
}

export interface ExplainerVideoOutput {
  job_id: string;
  audience: AudienceType;
  language: LanguageCode;
  finish_used: FinishPreset;
  script_narration: string;
  video_url: string;
  subtitles_url: string;
  duration_sec: number;
}

export interface InstrumentProject {
  instrument_id: string;
  name: string;
  category: string;
  capture_source: "ZED_2I_STEREO_SVO2" | "PHONE_MULTIVIEW_MP4";
  status: "UPLOADED" | "PROCESSING_3D" | "READY_3D" | "RENDERING_VIDEO" | "COMPLETED";
  progress_pct: number;
  current_stage: string;
  mesh_glb_url?: string;
  gaussian_splat_url?: string;
  dimensions: InstrumentDimensions;
  hotspots: HotspotAnnotation[];
  explainer_videos: ExplainerVideoOutput[];
}
