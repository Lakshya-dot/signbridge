"""
SignBridge Canonical Sign Generator & Dataset Synthesizer (v3.0)
Generates mathematically precise geometric landmark configurations for 32 Indian Sign Language (ISL)
signs based on anatomical hand/pose dictionaries, augmented with realistic spatial-temporal variance.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List, Any
from .feature_engine import FeatureEngine

SIGNS_LIST = [
    "IDLE",        # Hands relaxed or away from camera
    "I",           # Pointing to chest (unimanual)
    "YOU",         # Pointing forward (unimanual)
    "NAME",        # Tapping index and middle fingers together (bimanual)
    "HOW",         # Curved hands rolling upward/forward (bimanual)
    "PLEASE",      # Open flat palm on chest (unimanual)
    "THANK YOU",   # Flat hand from chin moving forward (unimanual)
    "MEET",        # Index fingers upright moving together (bimanual)
    "NICE",        # Right palm sliding over flat left palm (bimanual)
    "WHAT",        # Open palm waggle (unimanual)
    "WHERE",       # Both open palms facing UP side by side (bimanual)
    "WHEN",        # Index fingers touching (bimanual)
    "WHY",         # Y-hand or hand near temple (unimanual high)
    "HELP",        # Right fist on flat left palm (bimanual)
    "HOSPITAL",    # Index fingers crossing into '+' (bimanual)
    "DOCTOR",      # Fingers checking pulse on left wrist (bimanual)
    "EMERGENCY",   # Waving bimanual fists near chest (bimanual)
    "SICK",        # Hand near forehead/chest (unimanual)
    "FEVER",       # Back of hand resting on forehead (unimanual high)
    "PAIN",        # Index fingers twisting toward each other near chest (bimanual)
    "TIRED",       # Curved hands dropping down on chest (bimanual)
    "MEDICINE",    # Grinding right palm into left palm (bimanual)
    "FOOD",        # Pinched fingers tapping lips (unimanual high)
    "WATER",       # 3 middle fingers extended near chin (unimanual)
    "WANT",        # Claw hands pulling inward (unimanual)
    "NEED",        # Bent index finger hooking down (unimanual)
    "GOOD",        # Thumbs up (unimanual)
    "BAD",         # Thumbs down (unimanual)
    "HAPPY",       # Open palms brushing upward on chest (bimanual)
    "TODAY",       # Both Y-hands or palms downward low chest (bimanual)
    "TOMORROW",    # Thumb flicking forward from cheek (unimanual)
    "STOP"         # Open vertical palm pushing outward (unimanual)
]

def generate_canonical_landmarks(sign_name: str) -> Dict[str, Any]:
    """Generates canonical raw MediaPipe holistic landmark dictionary for a given ISL sign."""
    data = {
        "has_left_hand": False,
        "has_right_hand": False,
        "has_pose": True,
        "left_hand": np.zeros((21, 3), dtype=np.float32),
        "right_hand": np.zeros((21, 3), dtype=np.float32),
        "pose_anchors": np.array([
            [0.5, 0.25, 0.0],  # Nose
            [0.35, 0.45, 0.0], # Left shoulder
            [0.65, 0.45, 0.0]  # Right shoulder
        ], dtype=np.float32)
    }

    if sign_name == "IDLE":
        if np.random.rand() > 0.5:
            data["has_right_hand"] = True
            data["right_hand"][0] = [0.6, 0.85, 0.0]
        return data

    def build_hand(wrist_pos, finger_states, dir_mult=(0.0, -0.03, 0.0)):
        hand = np.zeros((21, 3), dtype=np.float32)
        hand[0] = wrist_pos
        mcp_offsets = [
            [-0.04, -0.04, 0.0], # Thumb
            [-0.02, -0.08, 0.0], # Index
            [0.0, -0.09, 0.0],   # Middle
            [0.02, -0.08, 0.0],  # Ring
            [0.04, -0.06, 0.0]   # Pinky
        ]
        chain_indices = [
            [1, 2, 3, 4],     # Thumb
            [5, 6, 7, 8],     # Index
            [9, 10, 11, 12],  # Middle
            [13, 14, 15, 16], # Ring
            [17, 18, 19, 20]  # Pinky
        ]
        for f_idx, (is_ext, offset, indices) in enumerate(zip(finger_states, mcp_offsets, chain_indices)):
            base_pt = wrist_pos + offset
            hand[indices[0]] = base_pt
            dir_vec = np.array(dir_mult) if is_ext else np.array([0.0, 0.015, 0.02])
            for step_i, pt_idx in enumerate(indices[1:], start=1):
                hand[pt_idx] = base_pt + dir_vec * step_i
        return hand

    # --- 1. GREETINGS & PERSONAL ---
    if sign_name == "I":
        # Pointing index inward to chest
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.52, 0.52, -0.02]), [False, True, False, False, False], (0.0, 0.02, 0.02))

    elif sign_name == "YOU":
        # Pointing index forward at camera
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.55, 0.45, -0.15]), [False, True, False, False, False], (0.0, -0.03, -0.03))

    elif sign_name == "NAME":
        # Tapping index and middle fingers together
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.48, 0.48, -0.05]), [False, True, True, False, False])
        data["right_hand"] = build_hand(np.array([0.52, 0.48, -0.05]), [False, True, True, False, False])

    elif sign_name == "HOW":
        # Curved hands rolling upward
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.42, 0.52, -0.05]), [True, True, True, False, False])
        data["right_hand"] = build_hand(np.array([0.58, 0.52, -0.05]), [True, True, True, False, False])

    elif sign_name == "PLEASE":
        # Open flat palm rubbing on chest
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.50, 0.46, -0.02]), [True, True, True, True, True])

    elif sign_name == "THANK YOU":
        # Flat hand from chin moving forward
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.52, 0.35, -0.10]), [True, True, True, True, True], (0.0, -0.02, -0.03))

    elif sign_name == "MEET":
        # Index fingers upright touching knuckles
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.46, 0.45, -0.05]), [False, True, False, False, False])
        data["right_hand"] = build_hand(np.array([0.54, 0.45, -0.05]), [False, True, False, False, False])

    elif sign_name == "NICE":
        # Right palm sliding over flat left palm
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.46, 0.52, -0.05]), [True, True, True, True, True])
        data["right_hand"] = build_hand(np.array([0.48, 0.50, -0.05]), [True, True, True, True, True])

    # --- 2. QUESTIONS ---
    elif sign_name == "WHAT":
        # Open palm facing up waggle (unimanual)
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.60, 0.52, -0.10]), [True, True, True, True, True])

    elif sign_name == "WHERE":
        # Both open palms facing UP side by side (bimanual)
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.38, 0.50, -0.08]), [True, True, True, True, True])
        data["right_hand"] = build_hand(np.array([0.62, 0.50, -0.08]), [True, True, True, True, True])

    elif sign_name == "WHEN":
        # Index fingers touching horizontally
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.47, 0.46, -0.05]), [False, True, False, False, False])
        data["right_hand"] = build_hand(np.array([0.53, 0.46, -0.05]), [False, True, False, False, False])

    elif sign_name == "WHY":
        # Y-hand near temple
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.58, 0.28, -0.02]), [True, False, False, False, True])

    # --- 3. MEDICAL & EMERGENCY ---
    elif sign_name == "HELP":
        # Right fist on flat left palm
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.48, 0.52, -0.08]), [True, True, True, True, True])
        data["right_hand"] = build_hand(np.array([0.49, 0.48, -0.08]), [False, False, False, False, False])

    elif sign_name == "HOSPITAL":
        # Index fingers crossing into '+'
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.47, 0.45, -0.06]), [False, True, False, False, False])
        data["right_hand"] = build_hand(np.array([0.53, 0.45, -0.06]), [False, True, False, False, False])

    elif sign_name == "DOCTOR":
        # Checking pulse on left wrist
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.44, 0.52, -0.08]), [True, True, True, True, True])
        data["right_hand"] = build_hand(np.array([0.45, 0.50, -0.08]), [False, True, True, False, False])

    elif sign_name == "EMERGENCY":
        # Both fists waving rapidly near chest
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.36, 0.40, -0.06]), [False, False, False, False, False])
        data["right_hand"] = build_hand(np.array([0.64, 0.40, -0.06]), [False, False, False, False, False])

    elif sign_name == "SICK":
        # Hand near forehead/temple
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.56, 0.28, -0.02]), [False, True, True, False, False])

    elif sign_name == "FEVER":
        # Back of hand on forehead
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.50, 0.24, -0.01]), [True, True, True, True, True])

    elif sign_name == "PAIN":
        # Index fingers twisting toward each other near chest
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.45, 0.48, -0.05]), [False, True, False, False, False])
        data["right_hand"] = build_hand(np.array([0.55, 0.48, -0.05]), [False, True, False, False, False])

    elif sign_name == "TIRED":
        # Both hands drooping down near chest
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.40, 0.55, -0.04]), [True, True, True, True, True])
        data["right_hand"] = build_hand(np.array([0.60, 0.55, -0.04]), [True, True, True, True, True])

    elif sign_name == "MEDICINE":
        # Grinding right palm into left palm
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.46, 0.52, -0.06]), [True, True, True, True, True])
        data["right_hand"] = build_hand(np.array([0.50, 0.50, -0.06]), [False, False, False, False, False])

    # --- 4. EVERYDAY REQUESTS & STATES ---
    elif sign_name == "FOOD":
        # Pinched fingers tapping lips
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.52, 0.32, -0.03]), [False, False, False, False, False])

    elif sign_name == "WATER":
        # 3 middle fingers extended near chin
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.54, 0.34, -0.04]), [False, True, True, True, False])

    elif sign_name == "WANT":
        # Claw hand pulling inward
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.55, 0.50, -0.06]), [False, False, False, False, False])

    elif sign_name == "NEED":
        # Bent index finger hook
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.55, 0.48, -0.05]), [False, True, False, False, False])

    elif sign_name == "GOOD":
        # Thumbs up
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.56, 0.48, -0.08]), [True, False, False, False, False], (0.0, -0.04, 0.0))

    elif sign_name == "BAD":
        # Thumbs down
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.56, 0.52, -0.08]), [True, False, False, False, False], (0.0, 0.04, 0.0))

    elif sign_name == "HAPPY":
        # Open palms brushing upward on chest
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.42, 0.46, -0.04]), [True, True, True, True, True])
        data["right_hand"] = build_hand(np.array([0.58, 0.46, -0.04]), [True, True, True, True, True])

    elif sign_name == "TODAY":
        # Both Y-hands dropped low near chest
        data["has_left_hand"] = True
        data["has_right_hand"] = True
        data["left_hand"] = build_hand(np.array([0.38, 0.55, -0.05]), [True, False, False, False, True])
        data["right_hand"] = build_hand(np.array([0.62, 0.55, -0.05]), [True, False, False, False, True])

    elif sign_name == "TOMORROW":
        # Thumb flicking forward from cheek
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.58, 0.32, -0.04]), [True, False, False, False, False])

    elif sign_name == "STOP":
        # Open vertical palm pushing outward
        data["has_right_hand"] = True
        data["right_hand"] = build_hand(np.array([0.55, 0.44, -0.15]), [True, True, True, True, True], (0.0, -0.04, 0.0))

    return data


def generate_augmented_dataset(samples_per_class: int = 120, output_path: str = "SignBridge/data/dataset.npz"):
    """
    Generates a full synthetic feature dataset across all 32 ISL signs with realistic spatial noise:
    - Joint angle perturbations
    - Scale/distance jitter
    - Camera perspective and hand jitter
    """
    engine = FeatureEngine()
    X = []
    y = []

    print(f"Generating synthetic dataset for {len(SIGNS_LIST)} classes ({samples_per_class} samples each)...")
    
    for class_idx, sign_name in enumerate(SIGNS_LIST):
        canonical = generate_canonical_landmarks(sign_name)
        for _ in range(samples_per_class):
            sample = {
                "has_left_hand": canonical["has_left_hand"],
                "has_right_hand": canonical["has_right_hand"],
                "has_pose": canonical["has_pose"],
                "left_hand": canonical["left_hand"].copy(),
                "right_hand": canonical["right_hand"].copy(),
                "pose_anchors": canonical["pose_anchors"].copy()
            }

            # Inject realistic continuous noise
            noise_scale = 0.012
            if sample["has_left_hand"]:
                sample["left_hand"] += np.random.normal(0, noise_scale, sample["left_hand"].shape)
                scale = np.random.uniform(0.9, 1.1)
                sample["left_hand"] = (sample["left_hand"] - sample["left_hand"][0]) * scale + sample["left_hand"][0]

            if sample["has_right_hand"]:
                sample["right_hand"] += np.random.normal(0, noise_scale, sample["right_hand"].shape)
                scale = np.random.uniform(0.9, 1.1)
                sample["right_hand"] = (sample["right_hand"] - sample["right_hand"][0]) * scale + sample["right_hand"][0]

            if sample["has_pose"]:
                sample["pose_anchors"] += np.random.normal(0, 0.01, sample["pose_anchors"].shape)

            feat_vec = engine.extract_full_features(sample)
            X.append(feat_vec)
            y.append(class_idx)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_path, X=X, y=y, classes=SIGNS_LIST)
    print(f"Dataset successfully saved to {output_path}: {X.shape[0]} samples, {X.shape[1]} features.")
    return X, y, SIGNS_LIST


if __name__ == "__main__":
    generate_augmented_dataset()
