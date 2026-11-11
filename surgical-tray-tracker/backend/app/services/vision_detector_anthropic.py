import os
import base64
import json
import mimetypes
from anthropic import Anthropic
from typing import List
from app.models.schemas import InstrumentItem, TrayAuditResponse

# Initialize Anthropic Client
# Ensure ANTHROPIC_API_KEY is set in your environment
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def get_image_info(image_path: str):
    """Detect mime type and encode image."""
    mime_type, _ = mimetypes.guess_type(image_path)
    mime_type = mime_type or 'image/jpeg'
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded, mime_type

def analyze_tray_with_anthropic(image_path: str, manifest: List[InstrumentItem], tray_id: str) -> TrayAuditResponse:
    base64_image, media_type = get_image_info(image_path)

    # Serialize manifest to JSON string for the prompt
    manifest_json = json.dumps([item.model_dump() for item in manifest])

    prompt = f"""
    ROLE: You are a strict surgical instrument auditor.
    TASK: Audit the attached surgical tray image against the PROVIDED MANIFEST below.

    RULES:
    1. DO NOT change instrument names or IDs. Use only the IDs provided in the manifest.
    2. For every instrument in the manifest, look at the tray:
       - If you see the instrument clearly in the tray, mark it as 'present'.
       - If you see a slot/compartment that is empty or the instrument is missing, mark it as 'missing'.
       - If the instrument is in use or separated, mark it as 'in_use'.
    3. Return ONLY a valid JSON array of objects with keys: id, status, confidence.
       Example format:
       [
         {{"id": "inst-01", "status": "present", "confidence": 0.95}},
         {{"id": "inst-02", "status": "missing", "confidence": 0.85}}
       ]

    MANIFEST:
    {manifest_json}
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64_image}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    )

    # Extract and parse JSON from response
    try:
        content = response.content[0].text
        # Remove potential markdown code block markers
        json_str = content.replace("```json", "").replace("```", "").strip()
        updated_items = json.loads(json_str)
    except Exception as e:
        print(f"Error parsing Anthropic response: {e}")
        updated_items = []

    # Map back to InstrumentItem objects
    final_instruments = []
    for item in manifest:
        update = next((u for u in updated_items if u.get("id") == item.id), None)
        if update:
            item.status = update["status"]
            item.confidence = float(update.get("confidence", 0.9))
        final_instruments.append(item)

    # Recalculate totals
    present_count = sum(1 for i in final_instruments if i.status == "present")
    in_use_count = sum(1 for i in final_instruments if i.status == "in_use")
    missing_count = sum(1 for i in final_instruments if i.status == "missing")

    return TrayAuditResponse(
        tray_id=tray_id,
        surgery_type="Robotic / General Surgical Procedure",
        total_instruments=len(final_instruments),
        present_count=present_count,
        in_use_count=in_use_count,
        missing_count=missing_count,
        status="WARNING_MISSING_ITEM" if missing_count > 0 else "VERIFIED_COMPLETE",
        instruments=final_instruments
    )
