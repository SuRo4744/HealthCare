import os
import json
from typing import List
from app.models.schemas import InstrumentItem, TrayAuditResponse
from app.services.vision_detector import analyze_tray_against_manifest
from app.services.vision_detector_anthropic import analyze_tray_with_anthropic
from app.config import settings

def load_master_manifest() -> List[InstrumentItem]:
    manifest_path = os.path.join(settings.STORAGE_DIR, "master_manifest.json")
    if not os.path.exists(manifest_path):
        return [
            InstrumentItem(id="inst-01", name="Scalpel Handle #3", category="Cutting", status="present", confidence=0.98, usage_frequency_pct=98),
            InstrumentItem(id="inst-02", name="Metzenbaum Scissors", category="Cutting", status="present", confidence=0.95, usage_frequency_pct=92),
        ]
    with open(manifest_path, "r") as f:
        data = json.load(f)
        return [InstrumentItem(**item) for item in data]

def process_tray_image(image_path: str, tray_id: str) -> TrayAuditResponse:
    master_manifest = load_master_manifest()

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")

    # 1. Try Anthropic first if key exists
    if anthropic_key:
        try:
            print("Running audit using Anthropic Claude...")
            return analyze_tray_with_anthropic(image_path, master_manifest, tray_id)
        except Exception as e:
            print(f"Anthropic analysis failed: {e}")

    # 2. Try Google second if key exists
    if google_key:
        try:
            print("Running audit using Google Gemini...")
            return analyze_tray_against_manifest(image_path, master_manifest, tray_id)
        except Exception as e:
            print(f"Google analysis failed: {e}")

    # 3. Fallback: Audit Failed status if both keys fail or are missing
    print("WARNING: No valid API keys or all services failed. Audit not performed.")
    return TrayAuditResponse(
        tray_id=tray_id,
        surgery_type="Robotic / General Surgical Procedure",
        total_instruments=len(master_manifest),
        present_count=0,
        in_use_count=0,
        missing_count=len(master_manifest),
        status="CRITICAL_RETAINED_ALERT",
        instruments=master_manifest,
        annotated_image_url=f"/api/v1/tray/{tray_id}/annotated.jpg"
    )
