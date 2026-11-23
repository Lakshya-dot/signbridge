"""
SignBridge Assistive Communication Terminal (v3.5)
A human-centered, clinical-grade assistive communication platform bridging Deaf signers
and hearing non-signers using a standard laptop webcam and classical machine learning.

Designed specifically to address the core problem statement:
"Deaf and hard-of-hearing people often cannot communicate easily with people who do not know sign language,
and interpreters are scarce."
"""

import os
import sys
import time
import json
import threading
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, Response, jsonify, request, send_file, render_template_string
import webbrowser

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SignBridge.live_dashboard import SignBridgeDashboard

app = Flask(__name__)

# Global Dashboard Instance and Camera Frame Holder
dashboard = None
camera_lock = threading.Lock()
current_frame_bytes = None
is_running = True

def camera_stream_worker():
    global current_frame_bytes, is_running, dashboard
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[SignBridge Web] Error: Camera 0 could not be opened.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("[SignBridge Web] Clean camera streaming pipeline initialized (Zero OpenCV overlay).")

    while is_running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)  # Mirror view
        # IMPORTANT: render_opencv_hud=False ensures clean video without small pixelated text!
        annotated = dashboard.process_frame(frame, render_opencv_hud=False)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 88])
        if ret:
            with camera_lock:
                current_frame_bytes = buffer.tobytes()

        # Slight pause to yield GIL and maintain smooth ~30 FPS
        time.sleep(0.005)

    cap.release()
    print("[SignBridge Web] Camera stream closed.")

def generate_mjpeg():
    global current_frame_bytes
    while is_running:
        with camera_lock:
            frame_data = current_frame_bytes
        if frame_data is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        time.sleep(0.03)

# ----------------- MODERN AESTHETIC FLOWY HTML -----------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="clinical">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SignBridge · Assistive Communication Terminal</title>
    <!-- Modern Sans & Native Indian Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@500;700;800&family=Noto+Sans+Telugu:wght@500;700;800&family=Noto+Sans+Tamil:wght@500;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        /* ================= COLOR THEMES ================= */
        :root[data-theme="clinical"] {
            --bg-base: #F8FAFB;
            --bg-surface: #FFFFFF;
            --bg-surface-subtle: #F1F5F7;
            --border-color: #E2E8F0;
            --border-highlight: #CBD5E1;
            --text-heading: #0F172A;
            --text-body: #334155;
            --text-muted: #64748B;
            
            --teal-deep: #0F3D39;        /* Primary Pine */
            --teal-surface: #E8F5F3;     /* Mint Tint */
            --teal-text: #0D332F;
            --teal-accent: #059669;
            
            --amber-warm: #D97706;       /* Warm Ochre */
            --amber-surface: #FEF3C7;    /* Warm Amber Tint */
            --amber-text: #92400E;
            
            --green-active: #10B981;
            --danger: #EF4444;
            --shadow-card: 0 4px 20px -2px rgba(15, 61, 57, 0.05), 0 0 0 1px rgba(0, 0, 0, 0.04);
            --shadow-hero: 0 12px 36px -4px rgba(15, 61, 57, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
            --shadow-float: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }

        :root[data-theme="dark"] {
            --bg-base: #0B111A;
            --bg-surface: #141C28;
            --bg-surface-subtle: #1C2638;
            --border-color: #27354A;
            --border-highlight: #3B4D66;
            --text-heading: #F8FAFC;
            --text-body: #CBD5E1;
            --text-muted: #94A3B8;
            
            --teal-deep: #10B981;
            --teal-surface: rgba(16, 185, 129, 0.12);
            --teal-text: #34D399;
            --teal-accent: #34D399;
            
            --amber-warm: #F59E0B;
            --amber-surface: rgba(245, 158, 11, 0.12);
            --amber-text: #FBBF24;
            
            --green-active: #10B981;
            --danger: #EF4444;
            --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.06);
            --shadow-hero: 0 12px 36px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08);
            --shadow-float: 0 10px 25px rgba(0, 0, 0, 0.5);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-body);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        /* ================= ELEGANT TOP BAR ================= */
        header {
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 36px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        }

        .brand-cluster {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-icon {
            width: 44px;
            height: 44px;
            background: var(--teal-deep);
            color: #FFFFFF;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(15, 61, 57, 0.2);
        }

        .brand-title {
            font-size: 21px;
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: -0.4px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-tag {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 3px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
            background: var(--teal-surface);
            color: var(--teal-text);
        }

        .brand-sub {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .nav-pill-btn {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-color);
            color: var(--text-heading);
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            text-decoration: none;
        }

        .nav-pill-btn:hover {
            border-color: var(--teal-deep);
            background: var(--teal-surface);
            color: var(--teal-text);
            transform: translateY(-1px);
        }

        .live-status-pill {
            background: var(--teal-surface);
            border: 1px solid rgba(15, 61, 57, 0.15);
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 700;
            color: var(--teal-text);
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'JetBrains Mono', monospace;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green-active);
            box-shadow: 0 0 8px var(--green-active);
            animation: pulseDot 1.8s infinite;
        }

        @keyframes pulseDot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.2); }
        }

        /* ================= MISSION STRIP ================= */
        .mission-strip {
            background: var(--teal-surface);
            border-bottom: 1px solid rgba(15, 61, 57, 0.1);
            padding: 10px 36px;
            font-size: 13px;
            color: var(--teal-text);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .mission-strip strong {
            font-weight: 700;
        }

        /* ================= FLOWY MAIN WORKSPACE ================= */
        main {
            padding: 28px 36px;
            max-width: 1540px;
            margin: 0 auto;
            width: 100%;
            display: grid;
            grid-template-columns: 1.18fr 0.82fr;
            gap: 28px;
            flex: 1;
        }

        @media (max-width: 1180px) {
            main { grid-template-columns: 1fr; }
        }

        /* Modern Flowy Cards */
        .flowy-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 24px;
            box-shadow: var(--shadow-card);
            display: flex;
            flex-direction: column;
            gap: 20px;
            position: relative;
        }

        .card-title-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .card-actor-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .actor-avatar {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
        }

        .actor-avatar.signer {
            background: var(--teal-surface);
            color: var(--teal-deep);
        }

        .actor-avatar.hearing {
            background: var(--amber-surface);
            color: var(--amber-warm);
        }

        .actor-name {
            font-size: 17px;
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: -0.3px;
        }

        .actor-desc {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
        }

        /* ================= HERO CAMERA STAGE (PRISTINE & LARGE) ================= */
        .camera-hero-stage {
            position: relative;
            width: 100%;
            background: #000000;
            border-radius: 16px;
            overflow: hidden;
            aspect-ratio: 16 / 9;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            border: 1px solid var(--border-color);
        }

        .camera-hero-stage img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        /* Floating Overlays on Camera */
        .camera-floating-hud {
            position: absolute;
            top: 16px;
            left: 16px;
            right: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            pointer-events: none;
        }

        .active-sign-badge {
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(12px);
            color: #FFFFFF;
            padding: 8px 18px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 800;
            letter-spacing: 0.3px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            display: inline-flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow-float);
        }

        .active-sign-badge strong {
            color: #38BDF8;
            font-family: 'JetBrains Mono', monospace;
            font-size: 18px;
        }

        .camera-hud-chips {
            display: flex;
            gap: 8px;
        }

        .cam-chip {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(10px);
            color: #E2E8F0;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Large Gesture Hold Confirmation Bar */
        .hold-confirmation-bar {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 14px 18px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .hold-bar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        .hold-track {
            width: 100%;
            height: 10px;
            background: var(--border-color);
            border-radius: 999px;
            overflow: hidden;
            position: relative;
        }

        .hold-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #10B981, #059669);
            border-radius: 999px;
            transition: width 0.1s linear;
        }

        /* ================= COMMITTED GLOSS STREAM ================= */
        .gloss-stream-box {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .stream-meta-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.8px;
        }

        .tokens-stream-flex {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            min-height: 44px;
        }

        .gloss-token-pill {
            background: var(--teal-surface);
            color: var(--teal-text);
            border: 1px solid rgba(15, 61, 57, 0.2);
            padding: 6px 14px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 15px;
            font-weight: 800;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            animation: tokenEnter 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes tokenEnter {
            from { opacity: 0; transform: scale(0.9) translateY(4px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        .token-separator {
            color: var(--text-muted);
            font-size: 12px;
        }

        /* ================= MULTILINGUAL TRANSLATION HERO CARD ================= */
        .translation-hero-card {
            background: linear-gradient(135deg, var(--teal-surface) 0%, rgba(255, 255, 255, 0.6) 100%);
            border: 1px solid rgba(15, 61, 57, 0.22);
            border-radius: 18px;
            padding: 22px 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            box-shadow: var(--shadow-card);
        }

        .hero-banner-label {
            font-size: 11px;
            font-weight: 800;
            color: var(--teal-deep);
            text-transform: uppercase;
            letter-spacing: 0.9px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .spoken-english-sentence {
            font-size: 26px;
            font-weight: 800;
            color: var(--text-heading);
            line-height: 1.3;
            letter-spacing: -0.4px;
        }

        .spoken-regional-sentence {
            font-size: 24px;
            font-weight: 700;
            color: var(--teal-deep);
            line-height: 1.4;
        }

        .grammar-footnote {
            font-size: 12px;
            color: var(--text-muted);
            font-style: italic;
        }

        /* Language Choice Row */
        .language-pills-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            padding-top: 6px;
        }

        .lang-options-group {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .lang-pill-btn {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-body);
            padding: 7px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
        }

        .lang-pill-btn:hover {
            border-color: var(--teal-deep);
        }

        .lang-pill-btn.active {
            background: var(--teal-deep);
            color: #FFFFFF;
            border-color: var(--teal-deep);
            box-shadow: 0 4px 10px rgba(15, 61, 57, 0.2);
        }

        /* ================= RIGHT COLUMN: HEARING PERSON / CLINICAL DESK ================= */
        .hearing-response-hero {
            background: linear-gradient(135deg, var(--amber-surface) 0%, rgba(255, 255, 255, 0.7) 100%);
            border: 1px solid rgba(217, 119, 6, 0.25);
            border-radius: 18px;
            padding: 22px 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow: var(--shadow-card);
        }

        .hearing-hero-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .mic-talk-button {
            background: var(--amber-warm);
            color: #FFFFFF;
            border: none;
            padding: 12px 22px;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 800;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            box-shadow: 0 6px 16px rgba(217, 119, 6, 0.3);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .mic-talk-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 22px rgba(217, 119, 6, 0.4);
        }

        .mic-talk-button.recording {
            background: var(--danger);
            animation: recordPulse 1.2s infinite;
        }

        @keyframes recordPulse {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
            70% { box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        .captions-readout-bubble {
            background: var(--bg-surface);
            border: 1px solid rgba(217, 119, 6, 0.3);
            border-radius: 12px;
            padding: 16px 18px;
            font-size: 20px;
            font-weight: 800;
            color: var(--amber-text);
            line-height: 1.4;
            min-height: 65px;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        }

        /* ================= CONVERSATION TIMELINE ================= */
        .chat-thread-container {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 250px;
            overflow-y: auto;
        }

        .chat-msg-row {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        .msg-meta-author {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .msg-bubble {
            padding: 10px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.45;
            max-width: 88%;
        }

        .chat-msg-row.signer {
            align-items: flex-start;
        }
        .chat-msg-row.signer .msg-meta-author {
            color: var(--teal-deep);
        }
        .chat-msg-row.signer .msg-bubble {
            background: var(--teal-surface);
            border: 1px solid rgba(15, 61, 57, 0.15);
            color: var(--text-heading);
            border-top-left-radius: 2px;
        }

        .chat-msg-row.hearing {
            align-items: flex-end;
        }
        .chat-msg-row.hearing .msg-meta-author {
            color: var(--amber-warm);
        }
        .chat-msg-row.hearing .msg-bubble {
            background: var(--amber-surface);
            border: 1px solid rgba(217, 119, 6, 0.25);
            color: var(--amber-text);
            border-top-right-radius: 2px;
        }

        /* ================= ACTION BUTTON MATRIX ================= */
        .utility-actions-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }

        .action-button-pill {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-heading);
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .action-button-pill:hover {
            border-color: var(--teal-deep);
            background: var(--bg-surface-subtle);
            transform: translateY(-1px);
        }

        .action-button-pill.primary-teal {
            background: var(--teal-deep);
            color: #FFFFFF;
            border-color: var(--teal-deep);
            box-shadow: 0 4px 12px rgba(15, 61, 57, 0.25);
        }

        .action-button-pill.primary-teal:hover {
            opacity: 0.95;
            box-shadow: 0 6px 18px rgba(15, 61, 57, 0.35);
        }

        /* ================= ISL TUTOR CHALLENGE CARD ================= */
        .tutor-hub-card {
            background: linear-gradient(135deg, #EDE9FE 0%, #F5F3FF 100%);
            border: 1px solid #DDD6FE;
            border-radius: 16px;
            padding: 18px 22px;
            display: none;
            flex-direction: column;
            gap: 10px;
        }

        .tutor-hub-card.active {
            display: flex;
        }

        .tutor-card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            color: #7C3AED;
            letter-spacing: 0.7px;
        }

        .tutor-target-name {
            font-size: 24px;
            font-weight: 800;
            color: #5B21B6;
        }

        .tutor-instruction-body {
            font-size: 14px;
            font-weight: 600;
            color: #4C1D95;
        }

        /* ================= FOOTER ================= */
        footer {
            background: var(--bg-surface);
            border-top: 1px solid var(--border-color);
            padding: 16px 36px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
        }

        .footer-tech-specs {
            display: flex;
            align-items: center;
            gap: 16px;
            font-family: 'JetBrains Mono', monospace;
        }

        /* ================= MODAL ================= */
        .modal-veil {
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(4px);
            z-index: 100;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }

        .modal-pane {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            max-width: 860px;
            width: 100%;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: var(--shadow-float);
        }

        .modal-header-row {
            padding: 20px 26px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .modal-scroll-area {
            padding: 24px 26px;
            overflow-y: auto;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
        }

        .dict-sign-box {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .dict-tag {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--teal-deep);
        }

        .dict-word {
            font-size: 16px;
            font-weight: 800;
            color: var(--text-heading);
        }

        .dict-how {
            font-size: 13px;
            color: var(--text-body);
        }
    </style>
</head>
<body>

    <!-- Header Navigation -->
    <header>
        <div class="brand-cluster">
            <div class="brand-icon">
                <i class="fa-solid fa-hands-asl-interpreting"></i>
            </div>
            <div>
                <h1 class="brand-title">
                    SignBridge
                    <span class="brand-tag">Assistive Terminal · v3.5</span>
                </h1>
                <p class="brand-sub">Bridging Deaf Signers and Hearing Non-Signers using Standard Laptop Webcam · Amrita RAI</p>
            </div>
        </div>

        <div class="header-actions">
            <button class="nav-pill-btn" onclick="toggleTheme()" id="themeToggleBtn" title="Toggle Clinical / Dark Theme">
                <i class="fa-solid fa-circle-half-stroke"></i> <span id="themeToggleText">Clinical Light</span>
            </button>

            <button class="nav-pill-btn" onclick="toggleAppMode()" id="appModeBtn" title="Switch between Translator & Tutor Hub">
                <i class="fa-solid fa-graduation-cap"></i> <span id="appModeText">Translate Mode</span>
            </button>

            <button class="nav-pill-btn" onclick="toggleSkeletonOverlay()" id="skelToggleBtn">
                <i class="fa-solid fa-bone"></i> <span id="skelToggleText">Skeleton: ON</span>
            </button>

            <button class="nav-pill-btn" onclick="toggleClassifierModel()" id="modelToggleBtn">
                <i class="fa-solid fa-microchip"></i> <span id="modelToggleText">Random Forest</span>
            </button>

            <div class="live-status-pill">
                <span class="live-dot"></span>
                <span id="fpsBadgeText">30 FPS</span>
            </div>
        </div>
    </header>

    <!-- Problem Statement Banner (Grounded in Exact Mission) -->
    <div class="mission-strip">
        <div>
            <i class="fa-solid fa-universal-access" style="margin-right: 8px;"></i>
            <strong>Core Problem Statement:</strong> Deaf and hard-of-hearing individuals often cannot communicate easily with hearing staff, and interpreters are scarce. SignBridge replaces scarce interpreters using a standard laptop webcam without gloves or special sensors.
        </div>
        <div>
            <span style="font-size: 11px; font-weight: 800; opacity: 0.85;">23RAI303 · FINAL END-SEM CAPSTONE</span>
        </div>
    </div>

    <!-- Main Dual-Actor Flowy Workspace -->
    <main>
        
        <!-- ================= LEFT COLUMN: DEAF SIGNER PORTAL ================= -->
        <div class="flowy-card">
            
            <div class="card-title-bar">
                <div class="card-actor-info">
                    <div class="actor-avatar signer">
                        <i class="fa-solid fa-hand"></i>
                    </div>
                    <div>
                        <div class="actor-name">Deaf Signer Portal</div>
                        <div class="actor-desc">Direction 1: Indian Sign Language to Spoken Voice & Text</div>
                    </div>
                </div>

                <div style="display: flex; gap: 8px;">
                    <span class="brand-tag" id="handPresenceTag">Hands: Detecting...</span>
                </div>
            </div>

            <!-- Pristine Camera Viewport (Zero pixelated OpenCV text) -->
            <div class="camera-hero-stage">
                <img src="/video_feed" alt="Clean Camera Viewport">

                <!-- Floating Overlays on Video -->
                <div class="camera-floating-hud">
                    <div class="active-sign-badge">
                        ACTIVE SIGN: <strong id="heroActiveSign">IDLE</strong>
                    </div>

                    <div class="camera-hud-chips">
                        <div class="cam-chip" id="confTag">Conf: 0%</div>
                        <div class="cam-chip" id="cooldownNotice" style="display: none; background: #D97706; color: #FFF;">
                            Cooldown Refractory
                        </div>
                    </div>
                </div>
            </div>

            <!-- Full-Width Gesture Hold Confirmation Gauge -->
            <div class="hold-confirmation-bar">
                <div class="hold-bar-header">
                    <span><i class="fa-solid fa-stopwatch"></i> Hold Gesture to Commit (~0.35s steady hold)</span>
                    <span id="holdPctNum" style="font-family: 'JetBrains Mono'; color: var(--teal-deep); font-weight: 800;">0%</span>
                </div>
                <div class="hold-track">
                    <div class="hold-fill" id="holdFillBar"></div>
                </div>
            </div>

            <!-- Committed Gesture Stream (Gloss Chips) -->
            <div class="gloss-stream-box">
                <div class="stream-meta-header">
                    <span><i class="fa-solid fa-layer-group"></i> Committed Sign Sequence</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="nav-pill-btn" style="padding: 4px 10px; font-size: 11px;" onclick="undoLastSign()">
                            <i class="fa-solid fa-rotate-left"></i> Undo Last
                        </button>
                        <button class="nav-pill-btn" style="padding: 4px 10px; font-size: 11px;" onclick="clearSentenceBuffer()">
                            <i class="fa-solid fa-trash"></i> Clear All
                        </button>
                    </div>
                </div>

                <div class="tokens-stream-flex" id="tokensContainer">
                    <span style="color: var(--text-muted); font-size: 13px;">Buffer empty. Form gestures steadily in front of the camera...</span>
                </div>
            </div>

            <!-- Synthesized Multilingual Translation Hero -->
            <div class="translation-hero-card">
                <div class="hero-banner-label">
                    <i class="fa-solid fa-volume-high"></i> Synthesized Translation (Spoken Aloud to Hearing Person)
                </div>

                <div class="spoken-english-sentence" id="spokenEnglishText">
                    "Ready. Begin signing..."
                </div>

                <div class="spoken-regional-sentence" id="spokenRegionalText" style="display: none;"></div>

                <div class="grammar-footnote" id="grammarRuleFootnote">
                    Rule: Awaiting gesture input sequence
                </div>

                <!-- Language Selector & Voice Action -->
                <div class="language-pills-row">
                    <div class="lang-options-group">
                        <button class="lang-pill-btn active" onclick="chooseLanguage('ENGLISH')" id="btn_ENGLISH">English</button>
                        <button class="lang-pill-btn" onclick="chooseLanguage('HINDI')" id="btn_HINDI">हिंदी (Hindi)</button>
                        <button class="lang-pill-btn" onclick="chooseLanguage('TELUGU')" id="btn_TELUGU">తెలుగు (Telugu)</button>
                        <button class="lang-pill-btn" onclick="chooseLanguage('TAMIL')" id="btn_TAMIL">தமிழ் (Tamil)</button>
                    </div>

                    <button class="action-button-pill primary-teal" onclick="triggerSpeechVoice()">
                        <i class="fa-solid fa-volume-high"></i> Speak Voice
                    </button>
                </div>
            </div>

        </div>

        <!-- ================= RIGHT COLUMN: HEARING PERSON / CLINICAL DESK ================= -->
        <div class="flowy-card">
            
            <div class="card-title-bar">
                <div class="card-actor-info">
                    <div class="actor-avatar hearing">
                        <i class="fa-solid fa-user-doctor"></i>
                    </div>
                    <div>
                        <div class="actor-name">Hearing Interlocutor Portal</div>
                        <div class="actor-desc">Direction 2: Doctor / Staff Voice to Live Visual Captions</div>
                    </div>
                </div>

                <span class="brand-tag" style="background: var(--amber-surface); color: var(--amber-text);">
                    Closed-Loop
                </span>
            </div>

            <!-- Hearing Person Acoustic Response Card -->
            <div class="hearing-response-hero">
                <div class="hearing-hero-head">
                    <span style="font-size: 12px; font-weight: 800; color: var(--amber-text); text-transform: uppercase; letter-spacing: 0.6px;">
                        <i class="fa-solid fa-microphone-lines"></i> Hearing Person's Spoken Reply
                    </span>

                    <button class="mic-talk-button" id="hearingMicBtn" onclick="triggerHearingMic()">
                        <i class="fa-solid fa-microphone"></i>
                        <span id="hearingMicBtnText">Press to Speak</span>
                    </button>
                </div>

                <!-- Live Subtitles Display for Deaf Signer -->
                <div>
                    <div style="font-size: 11px; font-weight: 700; color: var(--amber-text); margin-bottom: 6px;">
                        LIVE SUBTITLES FOR DEAF USER:
                    </div>
                    <div class="captions-readout-bubble" id="hearingCaptionsBubble">
                        "Hearing person: Click 'Press to Speak' and talk into laptop mic..."
                    </div>
                </div>
            </div>

            <!-- ISL Tutor Challenge Module (Mode [T]) -->
            <div class="tutor-hub-card" id="tutorHubCard">
                <div class="tutor-card-meta">
                    <span><i class="fa-solid fa-award"></i> Hospital Staff ISL Training Challenge</span>
                    <span id="tutorScoreNum" style="font-size: 13px; font-weight: 800; color: #059669;">Score: 0 pts</span>
                </div>
                <div class="tutor-target-name" id="tutorTargetSign">SIGN: "HELP"</div>
                <div class="tutor-instruction-body" id="tutorInstructionStep">Rest your RIGHT fist on top of flat LEFT palm.</div>
            </div>

            <!-- Clinical Consultation Dialogue Timeline -->
            <div class="gloss-stream-box" style="flex: 1;">
                <div class="stream-meta-header">
                    <span><i class="fa-solid fa-comments"></i> Clinical Dialogue Timeline</span>
                    <span style="font-size: 11px; color: var(--text-muted);">Timestamped Log</span>
                </div>

                <div class="chat-thread-container" id="chatThreadBox">
                    <div class="chat-msg-row signer">
                        <span class="msg-meta-author">[SYSTEM] Session Initialized</span>
                        <div class="msg-bubble">
                            SignBridge terminal ready. Begin gesturing or press microphone to respond.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Utility Action Bar -->
            <div class="utility-actions-row">
                <button class="action-button-pill primary-teal" onclick="triggerSpeechVoice()">
                    <i class="fa-solid fa-play"></i> Voice Aloud
                </button>
                <button class="action-button-pill" onclick="downloadVisitTranscript()">
                    <i class="fa-solid fa-file-arrow-down"></i> Save Visit Log
                </button>
                <button class="action-button-pill" onclick="openDictionaryModal()">
                    <i class="fa-solid fa-book-medical"></i> 32-Sign Library
                </button>
            </div>

        </div>

    </main>

    <!-- Modal: 32-Class ISL Visual Dictionary -->
    <div class="modal-veil" id="dictModal" onclick="closeModalOnBackdrop(event)">
        <div class="modal-pane">
            <div class="modal-header-row">
                <h3 style="font-size: 19px; font-weight: 800; color: var(--text-heading); display: flex; align-items: center; gap: 10px;">
                    <i class="fa-solid fa-book-bookmark" style="color: var(--teal-deep);"></i>
                    32-Class ISL Clinical & Daily Life Dictionary
                </h3>
                <button class="nav-pill-btn" style="padding: 4px 10px;" onclick="closeDictionaryModal()">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>
            <div class="modal-scroll-area" id="dictGridContainer">
                <!-- Dynamically Populated -->
            </div>
        </div>
    </div>

    <!-- Technical Rigor Footer -->
    <footer>
        <div>
            <strong>SignBridge v3.5</strong> · Department of Robotics & AI · Amrita Vishwa Vidyapeetham
        </div>
        <div class="footer-tech-specs">
            <span><i class="fa-solid fa-bolt" style="color: var(--amber-warm);"></i> Latency: 2.8 ms (CPU)</span>
            <span><i class="fa-solid fa-cube"></i> 89-D Scale-Invariant Manifold</span>
            <span><i class="fa-solid fa-shield-halved" style="color: var(--green-active);"></i> Hysteresis State Machine</span>
        </div>
    </footer>

    <!-- Client-Side JavaScript -->
    <script>
        // Web Audio Harmonic Chimes
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playChime(freq = 520, type = 'sine') {
            try {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = type;
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.25);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.25);
            } catch(e) {}
        }

        // Theme Toggle: Clinical Light <-> Accessible Dark
        function toggleTheme() {
            const html = document.documentElement;
            const current = html.getAttribute('data-theme');
            const next = current === 'clinical' ? 'dark' : 'clinical';
            html.setAttribute('data-theme', next);
            document.getElementById('themeToggleText').innerText = next === 'clinical' ? 'Clinical Light' : 'Dark Mode';
            playChime(650);
        }

        // Real-Time Telemetry Polling Loop (120ms)
        let lastGlossesCount = 0;
        let lastTutorScore = 0;

        async function fetchTelemetry() {
            try {
                const res = await fetch('/api/telemetry');
                const data = await res.json();
                renderTelemetry(data);
            } catch (err) {
                console.error("Telemetry fetch error:", err);
            }
        }
        setInterval(fetchTelemetry, 120);

        function renderTelemetry(data) {
            // Header Stats
            document.getElementById('fpsBadgeText').innerText = `${data.fps} FPS`;
            document.getElementById('modelToggleText').innerText = data.active_model;
            document.getElementById('appModeText').innerText = data.mode === "TUTOR" ? "Tutor Training" : "Translate Mode";

            // Camera Overlays
            const activeSign = data.current_holding_sign !== "IDLE" ? data.current_holding_sign : (data.active_pred_sign || "IDLE");
            document.getElementById('heroActiveSign').innerText = activeSign;
            document.getElementById('confTag').innerText = `Conf: ${data.confidence || 0}%`;

            const cooldownEl = document.getElementById('cooldownNotice');
            cooldownEl.style.display = data.in_cooldown ? 'block' : 'none';

            // Hand presence
            const handPresence = (data.has_left_hand && data.has_right_hand) ? "Two Hands Active" :
                                 (data.has_left_hand ? "Left Hand Active" : 
                                 (data.has_right_hand ? "Right Hand Active" : "No Hands"));
            document.getElementById('handPresenceTag').innerText = handPresence;

            // Hold-to-Commit Progress Bar
            document.getElementById('holdFillBar').style.width = `${data.hold_pct}%`;
            document.getElementById('holdPctNum').innerText = `${data.hold_pct}%`;

            // Committed Sign Sequence (Gloss Chips)
            const tokensBox = document.getElementById('tokensContainer');
            if (data.gloss_sequence && data.gloss_sequence.length > 0) {
                let html = '';
                data.gloss_sequence.forEach((gloss, idx) => {
                    html += `<span class="gloss-token-pill">${gloss}</span>`;
                    if (idx < data.gloss_sequence.length - 1) {
                        html += `<i class="fa-solid fa-arrow-right token-separator"></i>`;
                    }
                });
                tokensBox.innerHTML = html;

                if (data.gloss_sequence.length > lastGlossesCount) {
                    playChime(720);
                }
                lastGlossesCount = data.gloss_sequence.length;
            } else {
                tokensBox.innerHTML = `<span style="color: var(--text-muted); font-size: 13px;">Buffer empty. Form gestures steadily in front of the camera...</span>`;
                lastGlossesCount = 0;
            }

            // Synthesized Translations
            document.getElementById('spokenEnglishText').innerText = `"${data.english_translation}"`;
            const regBox = document.getElementById('spokenRegionalText');
            if (data.regional_translation && data.current_lang !== "ENGLISH") {
                regBox.style.display = 'block';
                regBox.innerText = `"${data.regional_translation}"`;
            } else {
                regBox.style.display = 'none';
            }
            document.getElementById('grammarRuleFootnote').innerText = `Rule: ${data.current_rule}`;

            // Language Buttons Highlight
            ["ENGLISH", "HINDI", "TELUGU", "TAMIL"].forEach(l => {
                const btn = document.getElementById(`btn_${l}`);
                if (btn) {
                    if (l === data.current_lang) btn.classList.add('active');
                    else btn.classList.remove('active');
                }
            });

            // Hearing Speech Captions
            document.getElementById('hearingCaptionsBubble').innerText = `"${data.hearing_text}"`;
            const micBtn = document.getElementById('hearingMicBtn');
            const micBtnText = document.getElementById('hearingMicBtnText');
            if (data.is_listening) {
                micBtn.classList.add('recording');
                micBtnText.innerText = "Listening...";
            } else {
                micBtn.classList.remove('recording');
                micBtnText.innerText = "Press to Speak";
            }

            // Tutor Module Card
            const tutorCard = document.getElementById('tutorHubCard');
            if (data.mode === "TUTOR") {
                tutorCard.classList.add('active');
                document.getElementById('tutorTargetSign').innerText = `SIGN: "${data.tutor.target}"`;
                document.getElementById('tutorInstructionStep').innerText = data.tutor.instruction;
                document.getElementById('tutorScoreNum').innerText = `Score: ${data.tutor.score} pts`;

                if (data.tutor.score > lastTutorScore) {
                    playChime(880, 'triangle');
                }
                lastTutorScore = data.tutor.score;
            } else {
                tutorCard.classList.remove('active');
            }

            // Dialogue Timeline Chat
            if (data.recent_log && data.recent_log.length > 0) {
                const chatBox = document.getElementById('chatThreadBox');
                let chatHtml = '';
                data.recent_log.forEach(item => {
                    const isSigner = item.speaker === "DEAF SIGNER";
                    chatHtml += `
                        <div class="chat-msg-row ${isSigner ? 'signer' : 'hearing'}">
                            <span class="msg-meta-author">[${item.speaker}] ${item.time}</span>
                            <div class="msg-bubble">${item.text}</div>
                        </div>
                    `;
                });
                chatBox.innerHTML = chatHtml;
            }
        }

        // Action Handlers
        async function triggerSpeechVoice() {
            playChime(500);
            await fetch('/api/speak', { method: 'POST' });
        }

        async function triggerHearingMic() {
            playChime(620);
            await fetch('/api/listen', { method: 'POST' });
        }

        async function undoLastSign() {
            playChime(420);
            await fetch('/api/undo', { method: 'POST' });
        }

        async function clearSentenceBuffer() {
            playChime(320);
            await fetch('/api/clear', { method: 'POST' });
        }

        async function toggleAppMode() {
            playChime(750);
            await fetch('/api/toggle_mode', { method: 'POST' });
        }

        async function toggleClassifierModel() {
            playChime(700);
            await fetch('/api/toggle_model', { method: 'POST' });
        }

        async function toggleSkeletonOverlay() {
            playChime(580);
            const res = await fetch('/api/toggle_landmarks', { method: 'POST' });
            const data = await res.json();
            document.getElementById('skelToggleText').innerText = `Skeleton: ${data.landmarks ? 'ON' : 'OFF'}`;
        }

        async function chooseLanguage(langCode) {
            playChime(680);
            await fetch('/api/set_language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lang: langCode })
            });
        }

        function downloadVisitTranscript() {
            playChime(820);
            window.location.href = '/api/download_log';
        }

        // 32-Class ISL Clinical Dictionary
        const DICTIONARY_ITEMS = [
            { name: "HELP", tag: "2-Hand · Contact", desc: "Rest right fist on top of flat left palm. Core emergency sign." },
            { name: "HOSPITAL", tag: "2-Hand · Precision", desc: "Cross extended index fingers into a plus sign (+)." },
            { name: "DOCTOR", tag: "2-Hand · Relational", desc: "Tap right index & middle fingers onto left wrist (checking pulse)." },
            { name: "FEVER", tag: "1-Hand · Facial", desc: "Place back of open right hand onto forehead." },
            { name: "SICK", tag: "1-Hand · Deictic", desc: "Touch temple / forehead with extended right finger." },
            { name: "MEDICINE", tag: "2-Hand · Contact", desc: "Rub right thumb in circular grinding motion across flat left palm." },
            { name: "PAIN", tag: "2-Hand · Motion", desc: "Point both index fingers toward each other with twisting wrist motion." },
            { name: "EMERGENCY", tag: "2-Hand · Urgent", desc: "Wave both open hands rapidly horizontally across upper chest." },
            { name: "YOU", tag: "1-Hand · Directional", desc: "Point right index finger directly forward toward camera." },
            { name: "I", tag: "1-Hand · Inward", desc: "Point right index finger inward touching center of sternum/chest." },
            { name: "WHERE", tag: "2-Hand · Spatial", desc: "Raise both open hands side-by-side with palms facing upwards." },
            { name: "WHAT", tag: "1-Hand · Query", desc: "Open single hand facing up with gently curved fingers." },
            { name: "GOOD", tag: "1-Hand · Approval", desc: "Clear upright thumbs-up at chest level." },
            { name: "BAD", tag: "1-Hand · Disapproval", desc: "Thumbs-down gesture at chest level." },
            { name: "WATER", tag: "1-Hand · Survival", desc: "Form 'W' shape (3 fingers raised) and tap near chin." },
            { name: "FOOD", tag: "1-Hand · Daily", desc: "Touch all fingertips together and tap near mouth." },
            { name: "EAT", tag: "1-Hand · Action", desc: "Repetitive motion bringing fingertips toward mouth." },
            { name: "SLEEP", tag: "2-Hand · Posture", desc: "Place both flat palms together beside tilted head." },
            { name: "TODAY", tag: "2-Hand · Temporal", desc: "Form 'Y' hands (thumb+pinky) or drop palms low near chest." },
            { name: "TOMORROW", tag: "1-Hand · Forward", desc: "Touch thumb to cheek and rotate hand forward." },
            { name: "MEET", tag: "2-Hand · Interaction", desc: "Bring both upright index fingers together until knuckles touch." },
            { name: "THANK YOU", tag: "1-Hand · Politeness", desc: "Touch flat fingers to chin and move hand forward smoothly." },
            { name: "PLEASE", tag: "1-Hand · Courtesy", desc: "Circular rubbing motion with flat palm over chest." },
            { name: "STOP", tag: "2-Hand · Cessation", desc: "Chop edge of right hand down onto flat open left palm." },
            { name: "NEED", tag: "1-Hand · Request", desc: "Bent index finger hooked downward repeatedly." },
            { name: "WANT", tag: "2-Hand · Desire", desc: "Both cupped hands pulling inward toward chest." },
            { name: "HAPPY", tag: "2-Hand · Emotion", desc: "Brush both flat hands upward on chest twice." },
            { name: "SAD", tag: "1-Hand · Emotion", desc: "Drop open hand slowly down in front of face." },
            { name: "HOT", tag: "1-Hand · Sensory", desc: "Claw hand near mouth rotated outward." },
            { name: "COLD", tag: "2-Hand · Sensory", desc: "Both fists shaking near chest as if shivering." },
            { name: "WHY", tag: "1-Hand · Wh-Inquiry", desc: "Touch forehead and pull down into 'Y' hand shape." },
            { name: "HOW", tag: "2-Hand · Method", desc: "Roll both curved hands outward from palms-down to palms-up." }
        ];

        function openDictionaryModal() {
            playChime(600);
            const grid = document.getElementById('dictGridContainer');
            let html = '';
            DICTIONARY_ITEMS.forEach(s => {
                html += `
                    <div class="dict-sign-box">
                        <span class="dict-tag">${s.tag}</span>
                        <div class="dict-word">${s.name}</div>
                        <div class="dict-how">${s.desc}</div>
                    </div>
                `;
            });
            grid.innerHTML = html;
            document.getElementById('dictModal').style.display = 'flex';
        }

        function closeDictionaryModal() {
            document.getElementById('dictModal').style.display = 'none';
        }

        function closeModalOnBackdrop(e) {
            if (e.target.id === 'dictModal') {
                closeDictionaryModal();
            }
        }
    </script>
</body>
</html>
"""

# ----------------- FLASK ENDPOINTS -----------------

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/telemetry')
def api_telemetry():
    global dashboard
    if dashboard is None:
        return jsonify({})
    return jsonify(dashboard.get_telemetry())

@app.route('/api/speak', methods=['POST'])
def api_speak():
    global dashboard
    if dashboard:
        dashboard.speak_current()
    return jsonify({"status": "ok"})

@app.route('/api/listen', methods=['POST'])
def api_listen():
    global dashboard
    if dashboard:
        dashboard.start_listening_to_hearing()
    return jsonify({"status": "ok"})

@app.route('/api/clear', methods=['POST'])
def api_clear():
    global dashboard
    if dashboard:
        dashboard.reset_sentence()
    return jsonify({"status": "ok"})

@app.route('/api/undo', methods=['POST'])
def api_undo():
    global dashboard
    if dashboard:
        dashboard.undo_last_sign()
    return jsonify({"status": "ok"})

@app.route('/api/toggle_model', methods=['POST'])
def api_toggle_model():
    global dashboard
    if dashboard:
        dashboard.toggle_model()
    return jsonify({"status": "ok", "model": dashboard.active_model_name})

@app.route('/api/toggle_mode', methods=['POST'])
def api_toggle_mode():
    global dashboard
    if dashboard:
        dashboard.toggle_mode()
    return jsonify({"status": "ok", "mode": dashboard.mode})

@app.route('/api/toggle_landmarks', methods=['POST'])
def api_toggle_landmarks():
    global dashboard
    if dashboard:
        dashboard.show_landmarks = not dashboard.show_landmarks
    return jsonify({"status": "ok", "landmarks": dashboard.show_landmarks})

@app.route('/api/set_language', methods=['POST'])
def api_set_language():
    global dashboard
    data = request.get_json() or {}
    lang = data.get("lang", "ENGLISH")
    if dashboard:
        dashboard.set_language(lang)
    return jsonify({"status": "ok", "language": dashboard.current_lang})

@app.route('/api/download_log')
def api_download_log():
    global dashboard
    if dashboard:
        dashboard.export_session_log()
    log_path = os.path.abspath("SignBridge_Session_Log.txt")
    if os.path.exists(log_path):
        return send_file(log_path, as_attachment=True, download_name="SignBridge_Consultation_Record.txt")
    return "Log file not generated yet", 404

def launch_web_studio(port=5000):
    global dashboard, is_running
    dashboard = SignBridgeDashboard()

    # Start camera worker thread
    cam_thread = threading.Thread(target=camera_stream_worker, daemon=True)
    cam_thread.start()

    # Auto-open browser after 1.5 seconds
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://127.0.0.1:{port}")
    
    threading.Thread(target=open_browser, daemon=True).start()

    print("\n" + "="*70)
    print("  SignBridge v3.5: Assistive Communication Terminal Online")
    print(f"  Live URL: http://127.0.0.1:{port}")
    print("="*70 + "\n")

    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    finally:
        is_running = False

if __name__ == "__main__":
    launch_web_studio()
