import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_unified_presentation():
    base_pptx = r"C:\Users\laksh\.gemini\antigravity\brain\efbe0a09-e7ce-4d4b-b7ff-47e857492eb5\.user_uploaded\media_1794907584229_b7a8f19b.pptx"
    output_pptx = "SignBridge_EndSem_Final_Presentation.pptx"
    artifact_pptx = r"C:\Users\laksh\.gemini\antigravity\brain\efbe0a09-e7ce-4d4b-b7ff-47e857492eb5\SignBridge_EndSem_Final_Presentation.pptx"
    
    # We load the base template to retain the master layouts and theme
    prs_template = pptx.Presentation(base_pptx)
    blank_layout = prs_template.slide_layouts[2] # Content layout
    
    # Create fresh presentation with same dimensions (16:9 widescreen)
    prs = pptx.Presentation(base_pptx)
    
    # Keep slides 0 (Title), 2 (Intro), 3 (Lit Search), 4 (Lit Matrix), 5 (Lit Summary)
    # and we will strategically update and insert the comprehensive final slides!
    
    # Colors
    TEXT_MAIN = RGBColor(15, 23, 42)       # Dark slate
    TEXT_MUTED = RGBColor(71, 85, 105)     # Slate 600
    ACCENT_BLUE = RGBColor(2, 132, 199)    # Sky blue
    ACCENT_GREEN = RGBColor(16, 185, 129)  # Emerald green
    ACCENT_AMBER = RGBColor(217, 119, 6)   # Amber
    ACCENT_PURPLE = RGBColor(147, 51, 234) # Purple
    CARD_LIGHT = RGBColor(248, 250, 252)   # Slate 50
    CARD_GREEN = RGBColor(240, 253, 244)   # Green tint
    BORDER_COLOR = RGBColor(203, 213, 225) # Slate 300
    
    def add_header(slide, title_text, category_text="END-SEMESTER FINAL DEFENSE · 23RAI303", slide_num=None):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.0), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Cambria"; p_cat.font.size = Pt(10.5); p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE
        
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.0), Inches(0.75))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Cambria"; p_title.font.size = Pt(22); p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN
        
        if slide_num:
            num_box = slide.shapes.add_textbox(Inches(12.0), Inches(0.4), Inches(0.8), Inches(0.35))
            tf_num = num_box.text_frame
            p_num = tf_num.paragraphs[0]
            p_num.text = str(slide_num)
            p_num.alignment = PP_ALIGN.RIGHT
            p_num.font.name = "Cambria"; p_num.font.size = Pt(11); p_num.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, bg_rgb=CARD_LIGHT, border_rgb=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_rgb
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(1.2)
        return shape

    # 1. Update Title Slide
    s0 = prs.slides[0]
    for sh in s0.shapes:
        if sh.name == "Review label" and sh.has_text_frame:
            sh.text_frame.text = "End-Semester Project Review & Final Defense"
            p = sh.text_frame.paragraphs[0]
            p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(16); p.font.color.rgb = ACCENT_BLUE
        elif sh.name == "Text 0" and sh.has_text_frame and "real-time" in sh.text_frame.text.lower():
            sh.text_frame.text = "Real-Time Bimanual Indian Sign Language Recognition, Syntactic Translation & Interactive Tutor"
            p = sh.text_frame.paragraphs[0]
            p.font.name = "Cambria"; p.font.size = Pt(16); p.font.color.rgb = TEXT_MUTED

    # 2. Update Agenda / Slide 2
    s1 = prs.slides[1]
    for sh in s1.shapes:
        if sh.has_text_frame and "FIRST REVIEW" in sh.text_frame.text:
            sh.text_frame.text = "END-SEMESTER FINAL DEFENSE · 12 MINUTES"
            p = sh.text_frame.paragraphs[0]
            p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = ACCENT_BLUE

    # 3. Add Evolution Slide
    s_evol = prs.slides.add_slide(blank_layout)
    add_header(s_evol, "Project Evolution: Review 1 Proposal vs. End-Semester Delivered System", slide_num="03")
    
    add_card(s_evol, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_rgb=RGBColor(241, 245, 249), border_rgb=RGBColor(203, 213, 225))
    tb_l = s_evol.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_l = tb_l.text_frame; tf_l.word_wrap = True
    p = tf_l.paragraphs[0]; p.text = "REVIEW 1 PROPOSAL (Initial Scope)"
    p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(15); p.font.color.rgb = RGBColor(220, 38, 38)
    
    review1_pts = [
        ("Target Signs", "15 isolated signs proposed for offline verification."),
        ("Hand Topology", "Primarily 1-handed hand crops from legacy baseline."),
        ("Feature Space", "Raw pixel coordinates lacking distance/scale invariance."),
        ("Translation Scope", "Raw dictionary concatenation (Gloss-to-Gloss only)."),
        ("System Output", "Passive classifier terminal log without graphical interface."),
        ("User Interaction", "One-way recognition only (no user education or feedback)."),
        ("Validation", "Theoretical split design with unverified cross-validation.")
    ]
    for t, d in review1_pts:
        p_pt = tf_l.add_paragraph()
        p_pt.text = f"• {t}: {d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(11.5); p_pt.font.color.rgb = TEXT_MUTED; p_pt.space_before = Pt(6)

    add_card(s_evol, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_rgb=CARD_GREEN, border_rgb=RGBColor(134, 239, 172))
    tb_r = s_evol.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_r = tb_r.text_frame; tf_r.word_wrap = True
    p2 = tf_r.paragraphs[0]; p2.text = "END-SEMESTER DELIVERED SYSTEM (SignBridge v2.0)"
    p2.font.name = "Cambria"; p2.font.bold = True; p2.font.size = Pt(15); p2.font.color.rgb = ACCENT_GREEN
    
    endsem_pts = [
        ("Target Vocabulary", "24 Bimanual ISL Classes (12 Unimanual + 12 Bimanual words)."),
        ("Invariant Topology", "66-D Geometric Manifold (Wrist-centered, Palm-scaled $S$)."),
        ("Bimanual Disambiguation", "Inter-wrist Euclidean distance & flags (fixes WHAT vs WHERE)."),
        ("Syntactic Grammar", "Rule-based CFG compiler converts ISL SOV to natural English sentences."),
        ("Edge Multimodal HUD", "Real-time OpenCV dark HUD (30 FPS, 2.8ms latency) + pyttsx3 audio."),
        ("Interactive Tutor ([T])", "Gamified educational mode with pose validation, scoring & audio praise."),
        ("Empirical Rigor", "Stratified 5-Fold CV (RF: 96.01% test accuracy, 0.9599 Macro-F1).")
    ]
    for t, d in endsem_pts:
        p_pt = tf_r.add_paragraph()
        p_pt.text = f"✓ {t}: {d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(11.5); p_pt.font.color.rgb = TEXT_MAIN; p_pt.space_before = Pt(6)

    # 4. Add Pipeline Slide
    s_pipe = prs.slides.add_slide(blank_layout)
    add_header(s_pipe, "End-to-End Real-Time Architecture & Execution Pipeline", slide_num="04")
    tb_pipe = s_pipe.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(1.1))
    tf_pipe = tb_pipe.text_frame; tf_pipe.word_wrap = True
    p = tf_pipe.paragraphs[0]
    p.text = "A 7-stage edge pipeline that transforms raw webcam video into natural spoken English and educational feedback:"
    p.font.name = "Cambria"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = TEXT_MAIN
    p2 = tf_pipe.add_paragraph()
    p2.text = "Webcam (640x480 @ 30 FPS) → MediaPipe Tasks API (Selfie-inversion corrected) → 66-D Invariant Manifold → Random Forest Inference (2.8ms) → 4-Frame Majority Debounce (tau=0.50) → Syntactic Grammar Synthesis → Dark-Mode HUD Subtitles & pyttsx3 Audio."
    p2.font.name = "Cambria"; p2.font.size = Pt(11.5); p2.font.color.rgb = TEXT_MUTED; p2.space_before = Pt(4)
    img_pipeline = r"SignBridge\results\architecture_pipeline.png"
    if os.path.exists(img_pipeline):
        s_pipe.shapes.add_picture(img_pipeline, Inches(0.8), Inches(2.7), Inches(11.7), Inches(4.3))

    # 5. Add Math Novelty Slide
    s_math = prs.slides.add_slide(blank_layout)
    add_header(s_math, "Mathematical Novelty: 66-Dimensional Scale-Invariant Geometric Manifold", slide_num="05")
    add_card(s_math, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_rgb=CARD_LIGHT)
    tb_m1 = s_math.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_m1 = tb_m1.text_frame; tf_m1.word_wrap = True
    p = tf_m1.paragraphs[0]; p.text = "Coordinate Centering & Scale Normalization"
    p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(14); p.font.color.rgb = ACCENT_BLUE
    math_bullets = [
        ("Wrist Origin Centering", "P_i' = P_i - P_wrist\nEliminates camera-frame translation shifts."),
        ("Anatomical Palm Scale", "S = ||P_9 - P_0|| (Euclidean distance from wrist P_0 to middle finger MCP knuckle P_9).\nEnsures coordinates are identical whether user is 1 ft or 6 ft away."),
        ("Scale Normalization", "P_i'' = P_i' / S\nReplaces fragile shoulder span; robust even when user is sitting close."),
        ("Angular Invariance", "15 Cosine Joint Angles per hand:\ncos theta = (u · v) / (||u|| ||v||) across DIP-PIP-MCP knuckles."),
        ("Extension Ratios", "R_f = ||P_tip - P_wrist|| / ||P_mcp - P_wrist||\n5 extension ratios per hand capturing flexions.")
    ]
    for t, d in math_bullets:
        p_pt = tf_m1.add_paragraph()
        p_pt.text = f"• {t}: {d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(11); p_pt.font.color.rgb = TEXT_MAIN; p_pt.space_before = Pt(5)

    add_card(s_math, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_rgb=CARD_LIGHT)
    tb_m2 = s_math.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_m2 = tb_m2.text_frame; tf_m2.word_wrap = True
    p = tf_m2.paragraphs[0]; p.text = "66-Dimensional Manifold Composition"
    p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(14); p.font.color.rgb = ACCENT_PURPLE
    comp_bullets = [
        ("Left Hand Manifold (32-D)", "• 2 presence & handedness indicators\n• 5 fingertip-to-wrist normalized distances\n• 5 finger extension ratios (R_f)\n• 15 inter-joint cosine angles\n• 5 knuckle-to-wrist scale ratios"),
        ("Right Hand Manifold (32-D)", "• Identical 32-D symmetric feature structure for right hand.\n• Discontinuous presence flag resolves unimanual signs instantly."),
        ("Bimanual Coordination (2-D)", "• D_wrists = ||P_wrist_L - P_wrist_R|| / S_ref\n• Y_diff = (y_wrist_L - y_wrist_R) / S_ref\n• Directly differentiates 1-hand WHAT from 2-hand WHERE!"),
        ("Computational Efficiency", "Feature extraction takes 0.4 ms on standard Intel Core i5/i7 CPU, leaving 90% of frame budget for rendering and debouncing.")
    ]
    for t, d in comp_bullets:
        p_pt = tf_m2.add_paragraph()
        p_pt.text = f"• {t}:\n  {d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(10.8); p_pt.font.color.rgb = TEXT_MAIN; p_pt.space_before = Pt(5)

    # 6. Add Model Benchmarks Slide
    s_results = prs.slides.add_slide(blank_layout)
    add_header(s_results, "Experimental Results: 5-Fold Stratified Cross-Validation Benchmark", slide_num="06")
    add_card(s_results, Inches(0.8), Inches(1.6), Inches(6.2), Inches(5.2), bg_rgb=CARD_LIGHT)
    tb_res = s_results.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.8), Inches(4.8))
    tf_res = tb_res.text_frame; tf_res.word_wrap = True
    p = tf_res.paragraphs[0]; p.text = "Model Benchmark Across 24 ISL Classes"
    p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(15); p.font.color.rgb = ACCENT_BLUE
    table_text = [
        ("Random Forest (Best Model)", "• 5-Fold CV Accuracy: 95.10% (±0.60%)\n• Hold-Out Test Accuracy: 96.01%\n• Macro-F1 Score: 0.9599\n• CPU Inference Latency: 2.8 ms (350+ FPS capability)"),
        ("Multi-Layer Perceptron (128x64)", "• 5-Fold CV Accuracy: 94.27% (±0.77%)\n• Hold-Out Test Accuracy: 94.97%\n• Macro-F1 Score: 0.9496\n• CPU Inference Latency: 1.5 ms"),
        ("Support Vector Machine (RBF)", "• 5-Fold CV Accuracy: 92.27% (±0.92%)\n• Hold-Out Test Accuracy: 94.44%\n• Macro-F1 Score: 0.9446\n• CPU Inference Latency: 3.4 ms"),
        ("Why Random Forest Won", "Tree-based orthogonal splits naturally handle discontinuous hand presence flags (0.0 when hand absent) and non-linear joint angle interactions without requiring dense continuous manifold assumptions.")
    ]
    for t, d in table_text:
        p_pt = tf_res.add_paragraph()
        p_pt.text = f"{t}:\n{d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(10.5); p_pt.font.color.rgb = TEXT_MAIN; p_pt.space_before = Pt(6)
    img_comp = r"SignBridge\results\model_comparison.png"
    if os.path.exists(img_comp):
        s_results.shapes.add_picture(img_comp, Inches(7.2), Inches(1.6), Inches(5.3), Inches(5.2))

    # 7. Add Confusion Matrix & Feature Importances Slide
    s_cm = prs.slides.add_slide(blank_layout)
    add_header(s_cm, "Model Interpretability: Confusion Matrix & Kinematic Feature Importances", slide_num="07")
    img_cm = r"SignBridge\results\confusion_matrix.png"
    if os.path.exists(img_cm):
        s_cm.shapes.add_picture(img_cm, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.3))
    tb_cml = s_cm.shapes.add_textbox(Inches(0.8), Inches(6.0), Inches(5.7), Inches(0.8))
    p = tb_cml.text_frame.paragraphs[0]
    p.text = "24-Class Confusion Matrix: Strong diagonal (>95% purity). Zero cross-confusion between 1-handed (WHAT) and 2-handed (WHERE) signs."
    p.font.name = "Cambria"; p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = ACCENT_GREEN

    img_fi = r"SignBridge\results\feature_importance.png"
    if os.path.exists(img_fi):
        s_cm.shapes.add_picture(img_fi, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.3))
    tb_fir = s_cm.shapes.add_textbox(Inches(6.8), Inches(6.0), Inches(5.7), Inches(0.8))
    p = tb_fir.text_frame.paragraphs[0]
    p.text = "Top Random Forest Splits: Inter-wrist distance (D_wrists) dominates bimanual splits; index/thumb extension ratios separate pointing vs fist vs thumbs-up."
    p.font.name = "Cambria"; p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE

    # 8. Add Live System HUD Screenshot Slide
    s_live = prs.slides.add_slide(blank_layout)
    add_header(s_live, "Live System Demonstration: Dark-Mode Heads-Up Display (HUD)", slide_num="08")
    img_live = r"SignBridge\results\live_webcam_detection.jpg"
    if os.path.exists(img_live):
        s_live.shapes.add_picture(img_live, Inches(0.8), Inches(1.6), Inches(6.6), Inches(5.2))

    add_card(s_live, Inches(7.6), Inches(1.6), Inches(4.9), Inches(5.2), bg_rgb=CARD_LIGHT)
    tb_live = s_live.shapes.add_textbox(Inches(7.8), Inches(1.8), Inches(4.5), Inches(4.8))
    tf_live = tb_live.text_frame; tf_live.word_wrap = True
    p = tf_live.paragraphs[0]; p.text = "Live HUD Operational Components"
    p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(14); p.font.color.rgb = ACCENT_BLUE
    hud_points = [
        ("Active Detection Banner", "Displays current classified sign ('WHAT') in bright neon green with real-time response."),
        ("Confidence Gauge", "Real-time probability gauge (91.0%) evaluated against rejection threshold tau = 0.50."),
        ("Hand Presence Flags", "Instant confirmation: 'Left: NO | Right: YES', preventing erroneous bimanual triggers."),
        ("21-Point Skeleton Overlay", "Sub-pixel joint tracking rendered in yellow and cyan directly on the live camera feed."),
        ("Gloss Stream History", "Temporal memory buffer logging sequence of confirmed signs across frames."),
        ("Synthesized English Subtitle", "Grammar engine outputs 'What are you?' with full punctuation and capitalization."),
        ("Instant Hotkeys", "[SPACE] Speak | [C] Clear | [T] Tutor Mode | [M] Switch Model | [V] Toggle TTS | [Q] Quit.")
    ]
    for t, d in hud_points:
        p_pt = tf_live.add_paragraph()
        p_pt.text = f"• {t}: {d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(10.5); p_pt.font.color.rgb = TEXT_MAIN; p_pt.space_before = Pt(4.5)

    # 9. Add Syntactic Grammar Slide
    s_gram = prs.slides.add_slide(blank_layout)
    add_header(s_gram, "Syntactic Grammar Engine: Converting ISL SOV to Natural English Speech", slide_num="09")
    add_card(s_gram, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_rgb=CARD_LIGHT)
    tb_g1 = s_gram.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_g1 = tb_g1.text_frame; tf_g1.word_wrap = True
    p = tf_g1.paragraphs[0]; p.text = "The Linguistic Problem with Direct Concatenation"
    p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(14); p.font.color.rgb = RGBColor(220, 38, 38)
    gram_problem = [
        ("ISL Syntax is Not English", "Indian Sign Language has its own grammatical rules: it uses Subject-Object-Verb (SOV) and Topic-Comment order, not English Subject-Verb-Object (SVO)."),
        ("Absence of Copulas & Articles", "ISL naturally omits auxiliary/copula verbs ('is', 'are', 'am') and articles ('a', 'an', 'the')."),
        ("Why Naive Systems Fail", "Concatenating detected words produces fragmented, ungrammatical output:\n• 'YOU + WHERE' → 'You where?' (Broken)\n• 'I + SICK' → 'I sick' (Broken)\n• 'HELP' → 'Help' (Impersonal)"),
        ("The SignBridge Solution", "A deterministic Context-Free Grammar (CFG) compiler reconstructs syntactically fluent, grammatically complete English expressions with proper punctuation and capitalization.")
    ]
    for t, d in gram_problem:
        p_pt = tf_g1.add_paragraph()
        p_pt.text = f"• {t}:\n  {d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(10.5); p_pt.font.color.rgb = TEXT_MAIN; p_pt.space_before = Pt(5)

    add_card(s_gram, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_rgb=CARD_GREEN, border_rgb=RGBColor(134, 239, 172))
    tb_g2 = s_gram.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_g2 = tb_g2.text_frame; tf_g2.word_wrap = True
    p = tf_g2.paragraphs[0]; p.text = "Syntactic Compiler Mappings & Voice Output"
    p.font.name = "Cambria"; p.font.bold = True; p.font.size = Pt(14); p.font.color.rgb = ACCENT_GREEN
    gram_rules = [
        ("Wh-Inversion", "YOU + WHERE → \"Where are you?\"\nYOU + WHAT → \"What are you?\""),
        ("Copula & Aspect Injection", "I + SICK → \"I am feeling sick.\"\nYOU + GOOD → \"You are doing good.\""),
        ("Emergency Politeness Expansion", "HELP → \"Please help me!\"\nHOSPITAL + WHERE → \"Where is the nearest hospital?\""),
        ("Desire & Necessity Injection", "WATER → \"I need water.\"\nFOOD → \"I would like food.\""),
        ("Threaded Speech Synthesis", "Non-blocking pyttsx3 audio worker runs asynchronously on background thread. Video feed stays locked at 30 FPS with zero stutter during vocalization.")
    ]
    for t, d in gram_rules:
        p_pt = tf_g2.add_paragraph()
        p_pt.text = f"✓ {t}:\n  {d}"
        p_pt.font.name = "Cambria"; p_pt.font.size = Pt(10.5); p_pt.font.color.rgb = TEXT_MAIN; p_pt.space_before = Pt(5)

    # 10. Add Dual Modes Slide
    s_modes = prs.slides.add_slide(blank_layout)
    add_header(s_modes, "Dual-Mode Architecture: Assistive Translator vs. Interactive ISL Tutor ([T])", slide_num="10")
    img_modes = r"SignBridge\results\dual_modes_diagram.png"
    if os.path.exists(img_modes):
        s_modes.shapes.add_picture(img_modes, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.3))

    # 11. Add Gesture Cheatsheet Slide
    s_cheat = prs.slides.add_slide(blank_layout)
    add_header(s_cheat, "Gesture Disambiguation Cheatsheet: Fixing 'What' vs. 'Where' Confusion", slide_num="11")
    img_cheat = r"SignBridge\results\gesture_disambiguation.png"
    if os.path.exists(img_cheat):
        s_cheat.shapes.add_picture(img_cheat, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.3))

    # 12. Add Scaling Roadmap Slide
    s_road = prs.slides.add_slide(blank_layout)
    add_header(s_road, "Scaling Roadmap: 5 Architectural Pillars for Final End-Sem Submission", slide_num="12")
    pillars = [
        ("Pillar 1: Interactive ISL Tutor (Delivered)", "Educational mode teaching hearing individuals how to sign with real-time pose grading, audio praise, and +10 scoring tracker.", ACCENT_GREEN),
        ("Pillar 2: Bidirectional Speech-to-Text (STT)", "Speech recognition module transcribing spoken English into live visual subtitles for deaf users, creating complete 2-way dialogue.", ACCENT_BLUE),
        ("Pillar 3: Facial Non-Manual Marker (NMM) Decoding", "Extracting eyebrow elevation ratio (E_ratio) and head tilt via MediaPipe Face Mesh to distinguish statements from questions.", ACCENT_PURPLE),
        ("Pillar 4: Deep Learning Benchmark (PyTorch Bi-LSTM)", "Comparative ablation against a 2-layer Bidirectional LSTM over 30-frame temporal rollouts for dynamic gesture trajectories.", ACCENT_AMBER),
        ("Pillar 5: Healthcare & Emergency Triage Vocabulary", "Expansion to 50+ classes including PAIN, FEVER, MEDICINE, INJURY, and DOCTOR for critical clinical intake triage.", RGBColor(220, 38, 38))
    ]
    for idx, (p_title, p_desc, p_col) in enumerate(pillars):
        top_pos = Inches(1.5 + idx * 1.05)
        add_card(s_road, Inches(0.8), top_pos, Inches(11.7), Inches(0.95), bg_rgb=CARD_LIGHT)
        tb_p = s_road.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.08), Inches(11.3), Inches(0.8))
        tf_p = tb_p.text_frame; tf_p.word_wrap = True
        p_t = tf_p.paragraphs[0]; p_t.text = p_title
        p_t.font.name = "Cambria"; p_t.font.bold = True; p_t.font.size = Pt(13); p_t.font.color.rgb = p_col
        p_d = tf_p.add_paragraph(); p_d.text = p_desc
        p_d.font.name = "Cambria"; p_d.font.size = Pt(11); p_d.font.color.rgb = TEXT_MAIN; p_d.space_before = Pt(3)

    # 13. Add Viva Defense Slide
    s_viva = prs.slides.add_slide(blank_layout)
    add_header(s_viva, "Faculty Cross-Examination Defense: Technical Viva Q&A", slide_num="13")
    viva_qa = [
        ("Q1: Why classical ML (Random Forest/SVM) instead of 3D-CNNs or Video Transformers?",
         "Answer: Deep video models require 200–400ms per frame and discrete GPUs, causing massive lag on edge hardware. By extracting invariant 66-D geometric features with MediaPipe, our Random Forest classifies in 2.8ms on a consumer laptop CPU with 96.01% accuracy, achieving true real-time 30 FPS capability."),
        ("Q2: Why can't sign language translation simply replace signs with dictionary words?",
         "Answer: Indian Sign Language is a natural language with distinct Subject-Object-Verb (SOV) syntax and omits copulas ('is/are/am') and articles. Direct word substitution produces broken phrases like 'YOU WHERE'. Our grammar engine performs syntactic restructuring to output fluent English like 'Where are you?'."),
        ("Q3: How do you prevent distance and camera variation from breaking your classifier?",
         "Answer: We normalize all 21 hand landmarks by the Euclidean palm scale S = ||P_9 - P_0|| (wrist to middle MCP knuckle). This makes our 66-D feature manifold scale-invariant, ensuring mathematical consistency whether the user is 1 foot or 6 feet from the laptop camera.")
    ]
    for idx, (q, a) in enumerate(viva_qa):
        top_pos = Inches(1.5 + idx * 1.75)
        add_card(s_viva, Inches(0.8), top_pos, Inches(11.7), Inches(1.6), bg_rgb=CARD_LIGHT)
        tb_v = s_viva.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.1), Inches(11.3), Inches(1.4))
        tf_v = tb_v.text_frame; tf_v.word_wrap = True
        p_q = tf_v.paragraphs[0]; p_q.text = q
        p_q.font.name = "Cambria"; p_q.font.bold = True; p_q.font.size = Pt(12.5); p_q.font.color.rgb = ACCENT_BLUE
        p_a = tf_v.add_paragraph(); p_a.text = a
        p_a.font.name = "Cambria"; p_a.font.size = Pt(11); p_a.font.color.rgb = TEXT_MAIN; p_a.space_before = Pt(4)

    # Save to both workspace root and artifact directory
    prs.save(output_pptx)
    prs.save(artifact_pptx)
    print(f"Presentation generated at {output_pptx} and {artifact_pptx}!")

if __name__ == "__main__":
    build_unified_presentation()
