from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def add_header(slide, tracker_text, title_text):
    # Top tracking / category
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = tracker_text.upper()
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0, 102, 204) # Deep Healthcare Blue

    # Main slide title
    tb2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = title_text
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(26, 38, 57) # Slate Dark

def create_card(slide, left, top, width, height, title, items, bg_color=RGBColor(245, 248, 250), border_color=RGBColor(210, 220, 230)):
    # Shape for background
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)

    # Text frame
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.3)
    tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.3)
    tf.margin_bottom = Inches(0.3)

    # Card Title
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(26, 38, 57)
    p.space_after = Pt(12)

    # Bullet items
    for item in items:
        p2 = tf.add_paragraph()
        if isinstance(item, tuple):
            # Header + subtext
            p2.text = f"{item[0]}: "
            p2.font.bold = True
            p2.font.size = Pt(13)
            p2.font.color.rgb = RGBColor(50, 65, 85)
            # Add normal text in same paragraph or separate
            run = p2.add_run()
            run.text = item[1]
            run.font.bold = False
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(70, 85, 105)
        else:
            p2.text = item
            p2.font.size = Pt(13)
            p2.font.color.rgb = RGBColor(70, 85, 105)
        p2.space_after = Pt(8)

def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # ==========================================
    # SLIDE 1: TITLE SLIDE (Dark Immersive Theme)
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = RGBColor(15, 23, 42) # Rich dark slate
    bg1.line.fill.background()

    # Title & Subtitle box
    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_tag = tf1.paragraphs[0]
    p_tag.text = "HEALTHCARE PRODUCT VISUALIZATION PLATFORM"
    p_tag.font.size = Pt(12)
    p_tag.font.bold = True
    p_tag.font.color.rgb = RGBColor(56, 189, 248) # Sky blue accent
    p_tag.space_after = Pt(16)

    p_title = tf1.add_paragraph()
    p_title.text = "From Video to 3D Model to Explainer Video"
    p_title.font.size = Pt(40)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(255, 255, 255)
    p_title.space_after = Pt(16)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Professional Pitch Deck & Full-Stack System Architecture"
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = RGBColor(148, 163, 184) # Muted slate

    # ==========================================
    # SLIDE 2: THE PROBLEM & SOLUTION
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Current State vs Platform Vision", "The Problem & Our Solution")

    problem_items = [
        ("Flat & Heavy", "Relying on 2D photos, static PDFs, and heavy physical demo kits."),
        ("Slow to Produce", "Explainer videos take weeks and expensive external creative agencies."),
        ("Expensive to Change", "3D models require costly scanners, CAD experts, and restarting for every update.")
    ]
    create_card(slide2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "The Healthcare Visualization Gap", problem_items, bg_color=RGBColor(254, 242, 242), border_color=RGBColor(254, 202, 202))

    solution_items = [
        ("Instant Transformation", "Turn a simple phone video or photo set into an interactive 3D Model and professional Explainer Video."),
        ("Zero CAD Required", "No specialized CAD engineers or expensive hardware scanners needed."),
        ("Infinite Adaptability", "Instant multi-language & audience adaptation (surgeons, patients, sales reps).")
    ]
    create_card(slide2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Our Comprehensive Solution", solution_items, bg_color=RGBColor(240, 253, 244), border_color=RGBColor(187, 247, 208))

    # ==========================================
    # SLIDE 3: COMPLETE SYSTEM ARCHITECTURE
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "System Architecture & Data Flow", "Mapping Frontend, Backend, & AI Processing")

    steps = [
        ("1. Frontend Portal", "Next.js 15 (App Router)\n• Landing Page (`/`)\n• Upload Portal (`/upload`)\n• 3D Canvas (`@react-three/fiber`)"),
        ("2. Backend API", "FastAPI (`app.py`)\n• REST API endpoints\n• Multipart form handling\n• Status polling endpoints"),
        ("3. AI Processing", "Background Workers\n• OpenCV SIFT Photogrammetry\n• Trimesh & SciPy Triangulation\n• MoviePy + PIL Video Renderer"),
        ("4. Artifact Output", "Local / Cloud Storage\n• 3D Models (`.obj`, `.glb`)\n• HD Explainer Videos (`.mp4`)\n• Structured JSON assets")
    ]

    card_w = Inches(2.7)
    card_h = Inches(5.0)
    start_x = Inches(0.8)
    gap = Inches(0.3)

    for i, (stitle, sdesc) in enumerate(steps):
        cx = start_x + i * (card_w + gap)
        # Parse lines
        lines = sdesc.split('\n')
        subtitle = lines[0]
        bullet_list = lines[1:]

        # Create card items format
        formatted_items = [subtitle] + bullet_list
        create_card(slide3, cx, Inches(1.8), card_w, card_h, stitle, formatted_items, bg_color=RGBColor(248, 250, 252), border_color=RGBColor(226, 232, 240))

    # ==========================================
    # SLIDE 4: TECHNOLOGY STACK & CORE MODULES
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Technology Stack & Core Modules", "Robust, Production-Ready Engineering")

    fe_tech = [
        ("Framework", "Next.js 15 (App Router) with TypeScript for type safety."),
        ("Styling", "Tailwind CSS for responsive modern healthcare UI."),
        ("3D Viewer", "React Three Fiber (`@react-three/fiber`) and Three.js for real-time model inspection.")
    ]
    create_card(slide4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Frontend Architecture", fe_tech)

    be_tech = [
        ("API Framework", "Python FastAPI for high-performance async processing."),
        ("3D Engine", "OpenCV (`cv2`) for SIFT feature detection and camera pose estimation; Trimesh & SciPy for point cloud triangulation and mesh exports (`.obj`, `.glb`)."),
        ("Video Engine", "MoviePy & Pillow (`PIL`) for automated slide rendering, title generation, annotations, and HD `.mp4` compilation.")
    ]
    create_card(slide4, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Backend & Processing Engines", be_tech)

    # ==========================================
    # SLIDE 5: BUSINESS IMPACT & FUTURE ROADMAP
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Value Proposition & Future Growth", "Business Impact & Roadmap")

    impact = [
        ("90% Cost Reduction", "Eliminate expensive CAD modeling, physical prototypes, and external creative agency fees."),
        ("10x Faster Time-to-Market", "Go from phone video to trained sales reps in minutes instead of weeks."),
        ("Infinite Scalability", "Instantly localize languages and tailor explanations for surgeons, patients, and trainers.")
    ]
    create_card(slide5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Key Business Impact", impact, bg_color=RGBColor(239, 246, 255), border_color=RGBColor(191, 219, 254))

    roadmap = [
        ("Phase 1 (Current)", "Core video upload, SIFT photogrammetry scaffolding, and multi-scene MoviePy video generation."),
        ("Phase 2", "Integration with production Gaussian Splatting / NeRF engines for photorealistic 3D fidelity."),
        ("Phase 3", "AI voiceover (Text-to-Speech) and multi-language script translation."),
        ("Phase 4", "Cloud object storage (AWS S3) and enterprise database persistence (PostgreSQL).")
    ]
    create_card(slide5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Strategic Roadmap", roadmap, bg_color=RGBColor(254, 243, 199), border_color=RGBColor(253, 230, 138))

    output_file = "Healthcare_Visualization_Presentation.pptx"
    prs.save(output_file)
    print(f"Professional presentation saved as {output_file}")

if __name__ == "__main__":
    main()
