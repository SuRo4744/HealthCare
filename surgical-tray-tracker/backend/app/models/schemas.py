from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class InstrumentItem(BaseModel):
    id: str
    name: str
    category: Literal["Cutting", "Grasping", "Retracting", "Clamping", "Suturing", "Scope / Robotic"]
    status: Literal["present", "in_use", "missing"]
    confidence: float
    usage_frequency_pct: int = Field(..., description="Percentage of surgeries where this tool is actually used")

class TrayAuditResponse(BaseModel):
    tray_id: str
    surgery_type: str
    total_instruments: int
    present_count: int
    in_use_count: int
    missing_count: int
    status: Literal["VERIFIED_COMPLETE", "WARNING_MISSING_ITEM", "CRITICAL_RETAINED_ALERT"]
    instruments: List[InstrumentItem]
    annotated_image_url: Optional[str] = None
