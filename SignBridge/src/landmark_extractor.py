"""
SignBridge Modern Landmark Extractor
Built on Google MediaPipe Tasks API (Python 3.12 compatible).
Extracts 3D landmarks for:
- Left hand (21 points)
- Right hand (21 points)
- Upper body pose anchors (Left shoulder, Right shoulder, Nose)
"""

import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Dict, Any

class LandmarkExtractor:
    def __init__(self,
                 hand_model_path: str = "SignBridge/models/hand_landmarker.task",
                 pose_model_path: str = "SignBridge/models/pose_landmarker.task",
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 **kwargs):

        if not os.path.exists(hand_model_path):
            raise FileNotFoundError(f"Hand landmarker model not found at {hand_model_path}")

        # 1. Initialize Hand Landmarker
        hand_base = python.BaseOptions(model_asset_path=hand_model_path)
        hand_opts = vision.HandLandmarkerOptions(
            base_options=hand_base,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.hand_detector = vision.HandLandmarker.create_from_options(hand_opts)

        # 2. Initialize Pose Landmarker
        self.pose_detector = None
        if os.path.exists(pose_model_path):
            pose_base = python.BaseOptions(model_asset_path=pose_model_path)
            pose_opts = vision.PoseLandmarkerOptions(
                base_options=pose_base,
                running_mode=vision.RunningMode.IMAGE
            )
            self.pose_detector = vision.PoseLandmarker.create_from_options(pose_opts)

        # Predefined hand connections for custom neon rendering
        self.hand_connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),        # Index
            (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
            (0, 13), (13, 14), (14, 15), (15, 16), # Ring
            (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
            (5, 9), (9, 13), (13, 17)              # Palm base
        ]

    def process_frame(self, bgr_frame: np.ndarray) -> Dict[str, Any]:
        """
        Processes a BGR image frame and returns extracted raw landmark arrays and presence flags.
        """
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        hand_result = self.hand_detector.detect(mp_image)
        pose_result = self.pose_detector.detect(mp_image) if self.pose_detector else None

        data = {
            "has_left_hand": False,
            "has_right_hand": False,
            "has_pose": False,
            "left_hand": np.zeros((21, 3), dtype=np.float32),
            "right_hand": np.zeros((21, 3), dtype=np.float32),
            "pose_anchors": np.zeros((3, 3), dtype=np.float32), # [Nose, Left_Shoulder, Right_Shoulder]
            "raw_hand_landmarks": []
        }

        # Parse Hands and Handedness
        if hand_result.hand_landmarks:
            data["raw_hand_landmarks"] = hand_result.hand_landmarks
            for lms, handedness in zip(hand_result.hand_landmarks, hand_result.handedness):
                side = handedness[0].category_name # "Left" or "Right"
                pts = np.array([[lm.x, lm.y, lm.z] for lm in lms], dtype=np.float32)

                # On horizontally-flipped (mirror/selfie) webcam frames, MediaPipe's handedness is inverted:
                actual_side = "Right" if side == "Left" else "Left"

                if actual_side == "Left":
                    data["has_left_hand"] = True
                    data["left_hand"] = pts
                else:
                    data["has_right_hand"] = True
                    data["right_hand"] = pts

        # Parse Pose Anchors
        if pose_result and pose_result.pose_landmarks and len(pose_result.pose_landmarks) > 0:
            pose_lms = pose_result.pose_landmarks[0]
            data["has_pose"] = True
            # 0: nose, 11: left_shoulder, 12: right_shoulder
            data["pose_anchors"][0] = [pose_lms[0].x, pose_lms[0].y, pose_lms[0].z]
            data["pose_anchors"][1] = [pose_lms[11].x, pose_lms[11].y, pose_lms[11].z]
            data["pose_anchors"][2] = [pose_lms[12].x, pose_lms[12].y, pose_lms[12].z]

        return data

    def draw_landmarks(self, frame: np.ndarray, data: Dict[str, Any]) -> np.ndarray:
        """Draws aesthetic neon landmarks and connections on the given frame."""
        h, w, _ = frame.shape

        # 1. Draw Hands
        for lms in data.get("raw_hand_landmarks", []):
            coords = [(int(lm.x * w), int(lm.y * h)) for lm in lms]

            # Draw bones
            for p1, p2 in self.hand_connections:
                cv2.line(frame, coords[p1], coords[p2], (0, 230, 255), 2, cv2.LINE_AA)

            # Draw joints
            for idx, (cx, cy) in enumerate(coords):
                if idx in [4, 8, 12, 16, 20]: # Fingertips
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 120), -1, cv2.LINE_AA)
                    cv2.circle(frame, (cx, cy), 7, (255, 255, 255), 1, cv2.LINE_AA)
                else:
                    cv2.circle(frame, (cx, cy), 3, (255, 100, 0), -1, cv2.LINE_AA)

        # 2. Draw Shoulder and Nose anchors if present
        if data.get("has_pose"):
            anchors = data["pose_anchors"]
            nose = (int(anchors[0][0] * w), int(anchors[0][1] * h))
            l_sh = (int(anchors[1][0] * w), int(anchors[1][1] * h))
            r_sh = (int(anchors[2][0] * w), int(anchors[2][1] * h))

            cv2.line(frame, l_sh, r_sh, (100, 255, 100), 2, cv2.LINE_AA)
            cv2.circle(frame, l_sh, 5, (0, 255, 0), -1)
            cv2.circle(frame, r_sh, 5, (0, 255, 0), -1)
            cv2.circle(frame, nose, 4, (0, 200, 255), -1)

        return frame

    def close(self):
        if hasattr(self, 'hand_detector') and self.hand_detector:
            self.hand_detector.close()
        if hasattr(self, 'pose_detector') and self.pose_detector:
            self.pose_detector.close()
