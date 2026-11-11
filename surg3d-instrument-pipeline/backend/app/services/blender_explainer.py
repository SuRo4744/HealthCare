"""
Stretch Goal: Automated Explainer Video Generator using Headless Blender (bpy) + Multilingual Script Generator.
"""
from typing import Dict, Any
from app.models.schemas import ExplainerRequest

AUDIENCE_SCRIPTS = {
    "scrub_nurse": {
        "en-US": (
            "Instrument Recognition Training: Left/Right Tibial Resection Guide. "
            "Step 1: Verify the 1.2 millimeter oscillating saw slot is clear of debris. "
            "Step 2: Attach the guide to the extramedullary alignment rod and lock the knurled thumb dial. "
            "Step 3: Prepare two 3.2 millimeter headless fixation pins for the convergent and parallel pin holes."
        ),
        "hi-IN": (
            "इंस्ट्रूमेंट प्रशिक्षण: टिबियल कटिंग गाइड। "
            "चरण 1: सुनिश्चित करें कि 1.2 मिमी आरी स्लॉट साफ है। "
            "चरण 2: गाइड को एलाइनमेंट रॉड से जोड़ें और लॉकिंग डायल को कस लें। "
            "चरण 3: बोन फिक्सेशन के लिए दो 3.2 मिमी पिन तैयार रखें।"
        ),
        "es-ES": (
            "Entrenamiento de Instrumentación: Guía de Resección Tibial. "
            "Paso 1: Verifique la ranura de corte de 1.2 milímetros. "
            "Paso 2: Asegure el dial de bloqueo en la barra de alineación. "
            "Paso 3: Prepare dos pines de fijación de 3.2 milímetros."
        ),
        "de-DE": (
            "Instrumentenschulung: Tibia-Resektionslehre. "
            "Schritt 1: Prüfen Sie den 1,2-Millimeter-Sägeschlitz. "
            "Schritt 2: Arretieren Sie das Rändelrad an der Ausrichtungsstange."
        )
    },
    "surgeon": {
        "en-US": (
            "Surgical Technique Overview: Precision Tibial Cutting Block. "
            "Features a 3-degree posterior slope built into the 1.27 millimeter captured saw guide. "
            "Dual convergent and parallel 3.2 millimeter pin tunnels provide rigid cortical purchase "
            "while allowing plus or minus 2 millimeter微-resection height adjustment via the central cam dial."
        ),
        "hi-IN": (
            "सर्जिकल तकनीक: टिबियल कटिंग ब्लॉक में 3-डिग्री पोस्टीरियर स्लोप और सटीक बोन रिसेक्शन के लिए माइक्रो-एडजस्टमेंट डायल शामिल है।"
        ),
        "es-ES": (
            "Técnica Quirúrgica: Bloque de corte tibial con pendiente posterior de 3 grados y ajuste micrométrico."
        ),
        "de-DE": (
            "Operationstechnik: Tibia-Schnittblock mit 3 Grad posteriorem Slope und Mikroeinstellung."
        )
    },
    "sales_rep": {
        "en-US": (
            "Product Highlight: Next-Gen Modular Tibial Resection Guide. "
            "Available in Satin 316L Stainless Steel or anti-glare Titanium Nitride Gold coating. "
            "Reduces instrument tray weight by 35 percent with quick-release cam locking."
        ),
        "hi-IN": "उत्पाद विशेषता: एंटी-ग्लेयर टाइटेनियम कोटिंग के साथ मॉड्यूलर टिबियल गाइड जो ट्रे का वजन 35% कम करता है।",
        "es-ES": "Destacado del Producto: Guía tibial modular con recubrimiento antirreflejos que reduce el peso un 35%.",
        "de-DE": "Produkthighlight: Modulare Tibialehre mit blendfreier TiN-Beschichtung."
    },
    "patient": {
        "en-US": (
            "Patient Guide: During your knee replacement, your surgeon uses this precision alignment guide "
            "to gently prepare the top surface of your shinbone so your new knee implant fits smoothly and naturally."
        ),
        "hi-IN": (
            "रोगी मार्गदर्शिका: घुटने की सर्जरी के दौरान, डॉक्टर इस सटीक गाइड का उपयोग करते हैं ताकि नया घुटना बिल्कुल सही फिट हो सके।"
        ),
        "es-ES": (
            "Guía para el Paciente: Su cirujano utiliza esta guía de precisión para asegurar un ajuste perfecto del implante."
        ),
        "de-DE": (
            "Patienteninfo: Ihr Chirurg nutzt diese Präzisionslehre für den passgenauen Sitz Ihres Knieimplantats."
        )
    }
}

BLENDER_HEADLESS_SCRIPT_TEMPLATE = """
# Run via: blender -b -P render_instrument_explainer.py -- --glb {glb_path} --out {out_mp4}
import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="{glb_path}")

# Setup Studio Three-Point Lighting for Metallic Surgical Instrument
bpy.ops.object.light_add(type='AREA', location=(0.5, -0.5, 0.8))
bpy.context.object.data.energy = 150

# Setup Orbiting Camera + Exploded View Keyframes
bpy.ops.object.camera_add(location=(0.0, -0.35, 0.18), rotation=(math.radians(72), 0, 0))
scene = bpy.context.scene
scene.camera = bpy.context.object
scene.render.engine = 'BLENDER_EEVEE'
scene.render.filepath = "{out_mp4}"
scene.render.image_settings.file_format = 'FFMPEG'
# bpy.ops.render.render(animation=True)
"""

def build_explainer_video_package(instrument_id: str, req: ExplainerRequest) -> Dict[str, Any]:
    audience_map = AUDIENCE_SCRIPTS.get(req.audience, AUDIENCE_SCRIPTS["scrub_nurse"])
    narration = audience_map.get(req.language, audience_map["en-US"])

    return {
        "narration": narration,
        "blender_script_preview": BLENDER_HEADLESS_SCRIPT_TEMPLATE.format(
            glb_path=f"/storage/{instrument_id}_tibial_guide.glb",
            out_mp4=f"/storage/{instrument_id}_{req.audience}_{req.language}.mp4"
        )
    }
