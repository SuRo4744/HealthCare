import os
import json
import mimetypes
from typing import List
import google.generativeai as genai
from app.models.schemas import InstrumentItem, TrayAuditResponse

def get_working_gemini_model():
    """
    Selects gemini-3.8-flash directly as explicitly requested by the Google API error message.
    """
    preferred_models = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest"
    ]

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for name in preferred_models:
            full = f"models/{name}"
            if full in available_models or name in available_models:
                print(f"Selected Gemini model: {name}")
                return genai.GenerativeModel(name)
    except Exception as e:
        print(f"Error querying models: {e}")

    print("Defaulting directly to gemini-3.8-flash")
    return genai.GenerativeModel("gemini-3.8-flash")

def analyze_tray_against_manifest(image_path: str, manifest: List[InstrumentItem], tray_id: str) -> TrayAuditResponse:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)

    mime_type, _ = mimetypes.guess_type(image_path)
    mime_type = mime_type or 'image/jpeg'

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    manifest_json = json.dumps([item.model_dump() for item in manifest])

    prompt = f"""
    ROLE: You are an expert surgical instrument auditor.
    TASK: Look carefully at the attached image of a surgical tray and audit it against the PROVIDED MANIFEST below.

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

    model = get_working_gemini_model()

    image_part = {
        "mime_type": mime_type,
        "data": image_bytes
    }

    print(f"Calling Gemini model ({model.model_name})...")
    response = model.generate_content([image_part, prompt])
    print("Gemini raw response received:")
    print(response.text[:300] + "..." if len(response.text) > 300 else response.text)

    content = response.text.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    updated_items = json.loads(content)

    final_instruments = []
    for item in manifest:
        update = next((u for u in updated_items if u.get("id") == item.id), None)
        if update:
            item.status = update["status"]
            item.confidence = float(update.get("confidence", 0.9))
        final_instruments.append(item)

    present_count = sum(1 for i in final_instruments if i.status == "present")
    in_use_count = sum(1 for i in final_instruments if i.status == "in_use")
    missing_count = sum(1 for i in final_instruments if i.status == "missing")

    print(f"Audit Summary for {tray_id}: Present={present_count}, In-Use={in_use_count}, Missing={missing_count}")

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
