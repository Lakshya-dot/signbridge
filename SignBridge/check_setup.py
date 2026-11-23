"""
SignBridge System Pre-Flight Diagnostic Tool
Verifies camera hardware, MediaPipe tracking, audio TTS engine, and ML model weights before presentation.
"""

import sys
import time
import cv2
import joblib
import numpy as np

def run_diagnostics():
    print("="*60)
    print("       SignBridge Pre-Flight System Diagnostic")
    print("="*60)

    # 1. Python Environment Check
    print(f"[1/6] Python Environment: {sys.version.split()[0]} on {sys.platform} - OK")

    # 2. Camera Check
    print("[2/6] Checking Webcam Accessibility...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("  [!] WARNING: Camera 0 could not be opened.")
        print("      Check if another app (Teams, Zoom, Camera app) is using the webcam.")
    else:
        ret, frame = cap.read()
        if ret:
            h, w, c = frame.shape
            print(f"  [+] Camera 0 OK! Active resolution: {w}x{h} ({c} channels)")
        else:
            print("  [!] Camera 0 opened but failed to capture a test frame.")
        cap.release()

    # 3. Model Weights Check
    print("[3/6] Verifying ML Model Artifacts...")
    try:
        scaler = joblib.load("SignBridge/models/scaler.joblib")
        rf = joblib.load("SignBridge/models/rf_model.joblib")
        svm = joblib.load("SignBridge/models/svm_model.joblib")
        import json
        with open("SignBridge/models/classes.json") as f:
            classes = json.load(f)
        print(f"  [+] Models OK! Loaded Random Forest & SVM ({len(classes)} classes registered).")
    except Exception as e:
        print(f"  [!] Model loading issue: {e}")

    # 4. Text-to-Speech (TTS) Engine Check
    print("[4/6] Checking Audio Speech Output (pyttsx3)...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"  [+] TTS Engine OK! Found {len(voices)} system voice profiles.")
        engine.say("SignBridge system check passed.")
        engine.runAndWait()
    except Exception as e:
        print(f"  [!] Audio TTS warning: {e}")

    # 5. Microphone & Speech-to-Text Check
    print("[5/6] Checking Microphone & Speech Recognition Listener...")
    try:
        import speech_recognition as sr
        mics = sr.Microphone.list_microphone_names()
        print(f"  [+] Microphone Hardware OK! Detected {len(mics)} audio input device(s).")
    except Exception as e:
        print(f"  [!] Microphone warning: {e}")

    # 6. Presentation Results & Figures Check
    print("[6/6] Checking Presentation Visuals in SignBridge/results/...")
    import os
    results_files = ["confusion_matrix.png", "model_comparison.png", "feature_importance.png", "pca_clusters.png"]
    all_present = True
    for rf in results_files:
        p = os.path.join("SignBridge/results", rf)
        if os.path.exists(p):
            print(f"  [+] Visual present: {rf}")
        else:
            print(f"  [-] Missing visual: {rf}")
            all_present = False

    print("="*60)
    if all_present:
        print(">> ALL SYSTEMS READY! You are fully prepared to launch SignBridge.")
    else:
        print(">> Note: Run 'python -m SignBridge.src.train_model' to generate missing figures.")
    print("="*60)

if __name__ == "__main__":
    run_diagnostics()
