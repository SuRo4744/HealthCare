export type InstrumentStatus = "present" | "in_use" | "missing";

export interface InstrumentItem {
  id: string;
  name: string;
  category: "Cutting" | "Grasping" | "Retracting" | "Clamping" | "Suturing" | "Scope / Robotic";
  status: InstrumentStatus;
  confidence: number;
  usage_frequency_pct: number;
}

export interface TrayAuditResponse {
  tray_id: string;
  surgery_type: string;
  total_instruments: number;
  present_count: number;
  in_use_count: number;
  missing_count: number;
  status: "VERIFIED_COMPLETE" | "WARNING_MISSING_ITEM" | "CRITICAL_RETAINED_ALERT";
  instruments: InstrumentItem[];
  annotated_image_url?: string;
}
