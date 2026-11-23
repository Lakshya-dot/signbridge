"""
SignBridge Interactive Data Collector
Enables signers to record real-time webcam samples of ISL signs for fine-tuning and evaluation.
Press [R] to record current sign for 3 seconds.
Press [N] to switch to the next sign.
Press [Q] to quit and save recorded samples.
"""

import os
import time
import json
import cv2
import numpy as np
from pathlib import Path

from .landmark_extractor import LandmarkExtractor
from .feature_engine import FeatureEngine
from .synthetic_data import SIGNS_LIST

def run_collector(output_path: str = "SignBridge/data/user_recorded.npz"):
    extractor = LandmarkExtractor(model_complexity=0)
    engine = FeatureEngine()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    current_idx = 1 # Skip IDLE by default
    recorded_X = []
    recorded_y = []

    recording = False
    record_start_time = 0.0
    record_duration = 2.5 # seconds
    sample_frames = []

    print("\n=== SignBridge Interactive Sign Collector ===")
    print("Controls:")
    print("  [R] - Start 2.5s recording for active sign")
    print("  [N] - Next sign")
    print("  [P] - Previous sign")
    print("  [Q] - Save & Exit")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        data = extractor.process_frame(frame)
        canvas = extractor.draw_landmarks(frame.copy(), data)

        current_sign = SIGNS_LIST[current_idx]
        now = time.time()

        # Handle recording state
        if recording:
            elapsed = now - record_start_time
            remaining = max(0.0, record_duration - elapsed)
            feat = engine.extract_full_features(data)
            sample_frames.append(feat)

            # Red recording indicator
            cv2.circle(canvas, (w - 50, 50), 20, (0, 0, 255), -1)
            cv2.putText(canvas, f"REC: {remaining:.1f}s", (w - 180, 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if elapsed >= record_duration:
                recording = False
                if sample_frames:
                    # Average or aggregate frames
                    mean_feat = np.mean(sample_frames, axis=0)
                    recorded_X.append(mean_feat)
                    recorded_y.append(current_idx)
                    print(f"Recorded sample for '{current_sign}'. Total recorded: {len(recorded_X)}")
                sample_frames = []
        else:
            # Standby UI header
            cv2.rectangle(canvas, (20, 20), (550, 110), (20, 20, 20), -1)
            cv2.putText(canvas, f"Target Sign: {current_sign} ({current_idx}/{len(SIGNS_LIST)-1})",
                        (35, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            cv2.putText(canvas, f"Press [R] to Record | [N] Next | [P] Prev | Total: {len(recorded_X)}",
                        (35, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.imshow("SignBridge - Sign Sample Collector", canvas)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('r') and not recording:
            recording = True
            record_start_time = time.time()
            sample_frames = []
        elif key == ord('n') and not recording:
            current_idx = (current_idx + 1) % len(SIGNS_LIST)
            if current_idx == 0:
                current_idx = 1
        elif key == ord('p') and not recording:
            current_idx = (current_idx - 1)
            if current_idx <= 0:
                current_idx = len(SIGNS_LIST) - 1

    cap.release()
    cv2.destroyAllWindows()
    extractor.close()

    if recorded_X:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(output_path, X=np.array(recorded_X), y=np.array(recorded_y), classes=SIGNS_LIST)
        print(f"\nSaved {len(recorded_X)} custom samples to {output_path}")
    else:
        print("No samples recorded.")


if __name__ == "__main__":
    run_collector()
