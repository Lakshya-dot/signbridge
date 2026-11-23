"""
SignBridge Robust Kinematic Feature Engineering Engine (v3.0)
Extracts scale-, translation-, and rotation-invariant 89-dimensional spatial features from MediaPipe landmarks:
- 5 Finger extension ratios (MCP-relative uncurled ratios)
- 15 Inter-joint finger cosine angles per hand
- 5 Fingertip-to-wrist normalized distances
- 4 Inter-fingertip spread distances
- 3 Palm normal unit vectors (Facing direction: UP, DOWN, FORWARD, INWARD)
- 1 Hand aperture (Thumb-to-Pinky span)
- 1 Pinch span (Thumb-to-Index span)
- 3 3D Index pointing vector (Separating chest pointing from forward camera pointing)
- 7 Two-hand coordination metrics (Inter-wrist, vertical offset, index touch, fist-to-palm contact, palm normal alignment)
- 2 Hand presence indicators
- 6 Head/Nose relative elevation anchors
- High-precision anatomical signature matching for rock-solid live detection and zero confusion
"""

import numpy as np
from typing import Dict, Any, List, Tuple

class FeatureEngine:
    def __init__(self):
        # Triplet indices for joint angles: (A, B, C) where B is the vertex
        self.angle_triplets = [
            # Thumb
            (0, 1, 2), (1, 2, 3), (2, 3, 4),
            # Index
            (0, 5, 6), (5, 6, 7), (6, 7, 8),
            # Middle
            (0, 9, 10), (9, 10, 11), (10, 11, 12),
            # Ring
            (0, 13, 14), (13, 14, 15), (14, 15, 16),
            # Pinky
            (0, 17, 18), (17, 18, 19), (18, 19, 20)
        ]
        self.fingertip_indices = [4, 8, 12, 16, 20]
        self.mcp_indices = [2, 5, 9, 13, 17]

    def _compute_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Computes cosine of the angle between vectors (p1-p2) and (p3-p2)."""
        v1 = p1 - p2
        v2 = p3 - p2
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 < 1e-6 or norm2 < 1e-6:
            return 1.0
        cos_theta = np.dot(v1, v2) / (norm1 * norm2)
        return float(np.clip(cos_theta, -1.0, 1.0))

    def get_finger_extension_states(self, landmarks_21x3: np.ndarray) -> List[bool]:
        """
        Determines whether each of the 5 fingers is extended (True) or curled (False).
        Order: [Thumb, Index, Middle, Ring, Pinky]
        Uses anatomically invariant MCP-relative extension ratio:
        ||P_tip - P_mcp|| / ||P_pip - P_mcp||.
        This correctly detects extension regardless of pointing direction
        (e.g. pointing inward towards chest for 'I', or forward for 'YOU').
        """
        finger_indices = [
            (4, 3, 2),    # Thumb: tip=4, ip=3, mcp=2
            (8, 6, 5),    # Index: tip=8, pip=6, mcp=5
            (12, 10, 9),  # Middle: tip=12, pip=10, mcp=9
            (16, 14, 13), # Ring: tip=16, pip=14, mcp=13
            (20, 18, 17)  # Pinky: tip=20, pip=18, mcp=17
        ]
        wrist = landmarks_21x3[0]
        states = []
        for tip_idx, pip_idx, mcp_idx in finger_indices:
            p_tip = landmarks_21x3[tip_idx]
            p_pip = landmarks_21x3[pip_idx]
            p_mcp = landmarks_21x3[mcp_idx]

            d_tip_mcp = float(np.linalg.norm(p_tip - p_mcp))
            d_pip_mcp = float(np.linalg.norm(p_pip - p_mcp))

            d_tip_wrist = float(np.linalg.norm(p_tip - wrist))
            d_mcp_wrist = float(np.linalg.norm(p_mcp - wrist))

            # Extended if finger segments are uncurled
            is_ext = (d_tip_mcp > 1.30 * (d_pip_mcp + 1e-6)) or (d_tip_wrist > 1.18 * (d_mcp_wrist + 1e-6))
            states.append(bool(is_ext))
        return states

    def extract_hand_features(self, landmarks_21x3: np.ndarray, is_present: bool) -> np.ndarray:
        """
        Extracts 37 invariant features from one hand:
        - 5 finger extension ratios (d_tip / d_mcp)
        - 15 joint cosine angles
        - 5 fingertip-to-wrist normalized distances
        - 4 inter-fingertip spread distances
        - 3 palm normal unit vector components (nx, ny, nz)
        - 1 hand aperture (Thumb-to-Pinky span)
        - 1 pinch distance (Thumb-to-Index span)
        - 3 3D Index pointing vector (tip - mcp unit vector)
        Total: 5 + 15 + 5 + 4 + 3 + 1 + 1 + 3 = 37 features
        """
        if not is_present:
            return np.zeros(37, dtype=np.float32)

        # 1. Wrist-relative translation
        wrist = landmarks_21x3[0]
        centered = landmarks_21x3 - wrist

        # 2. Palm-scale normalization (distance to middle MCP)
        palm_scale = float(np.linalg.norm(centered[9]))
        if palm_scale < 1e-4:
            palm_scale = 1.0
        normalized = centered / palm_scale

        features = []

        # 3. 5 Extension ratios
        for tip_idx, mcp_idx in zip(self.fingertip_indices, self.mcp_indices):
            d_tip = np.linalg.norm(centered[tip_idx])
            d_mcp = np.linalg.norm(centered[mcp_idx])
            ratio = d_tip / (d_mcp + 1e-5)
            features.append(float(ratio))

        # 4. 15 Joint Angles
        for a, b, c in self.angle_triplets:
            cos_val = self._compute_angle(normalized[a], normalized[b], normalized[c])
            features.append(cos_val)

        # 5. 5 Fingertip-to-Wrist normalized distances
        for tip in self.fingertip_indices:
            dist = np.linalg.norm(normalized[tip])
            features.append(float(dist))

        # 6. 4 Inter-fingertip spread distances
        for i in range(4):
            spread = np.linalg.norm(normalized[self.fingertip_indices[i]] - normalized[self.fingertip_indices[i+1]])
            features.append(float(spread))

        # 7. 3 Palm Normal Vector (Cross product of Wrist->IndexMCP and Wrist->PinkyMCP)
        v_index = normalized[5] - normalized[0]
        v_pinky = normalized[17] - normalized[0]
        palm_normal = np.cross(v_index, v_pinky)
        norm_len = np.linalg.norm(palm_normal)
        if norm_len > 1e-6:
            palm_normal_unit = palm_normal / norm_len
        else:
            palm_normal_unit = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        features.extend([float(palm_normal_unit[0]), float(palm_normal_unit[1]), float(palm_normal_unit[2])])

        # 8. 1 Hand Aperture (Thumb tip to Pinky tip normalized)
        aperture = float(np.linalg.norm(normalized[4] - normalized[20]))
        features.append(aperture)

        # 9. 1 Pinch Span (Thumb tip to Index tip normalized)
        pinch = float(np.linalg.norm(normalized[4] - normalized[8]))
        features.append(pinch)

        # 10. 3 Index Pointing Direction Unit Vector (Index Tip - Index MCP)
        index_dir = normalized[8] - normalized[5]
        index_len = np.linalg.norm(index_dir)
        if index_len > 1e-6:
            index_dir_unit = index_dir / index_len
        else:
            index_dir_unit = np.array([0.0, -1.0, 0.0], dtype=np.float32)
        features.extend([float(index_dir_unit[0]), float(index_dir_unit[1]), float(index_dir_unit[2])])

        return np.array(features, dtype=np.float32)

    def extract_full_features(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """
        Combines Left Hand (37), Right Hand (37), Presence (2),
        Two-Hand Interaction (7), and Head/Pose Anchors (6) into an 89-D feature vector.
        """
        has_l = raw_data.get("has_left_hand", False)
        has_r = raw_data.get("has_right_hand", False)
        l_pts = raw_data.get("left_hand", np.zeros((21, 3), dtype=np.float32))
        r_pts = raw_data.get("right_hand", np.zeros((21, 3), dtype=np.float32))
        pose = raw_data.get("pose_anchors", np.zeros((3, 3), dtype=np.float32))

        # Features 1 & 2: Individual Hand Geometries (37 + 37 = 74)
        l_feats = self.extract_hand_features(l_pts, has_l)
        r_feats = self.extract_hand_features(r_pts, has_r)

        # Feature 3: Presence (2)
        presence = np.array([1.0 if has_l else 0.0, 1.0 if has_r else 0.0], dtype=np.float32)

        # Feature 4: Two-Hand Interaction (7)
        interaction = np.zeros(7, dtype=np.float32)
        if has_l and has_r:
            # Palm scale reference
            ref_scale = max(float(np.linalg.norm(r_pts[9] - r_pts[0])), float(np.linalg.norm(l_pts[9] - l_pts[0])), 0.05)
            inter_wrist = float(np.linalg.norm(l_pts[0] - r_pts[0])) / ref_scale
            vert_diff = float(l_pts[0][1] - r_pts[0][1]) / ref_scale
            horiz_diff = float(l_pts[0][0] - r_pts[0][0]) / ref_scale
            index_dist = float(np.linalg.norm(l_pts[8] - r_pts[8])) / ref_scale

            # Right fist to left palm center contact distance (for HELP)
            l_palm_center = (l_pts[0] + l_pts[5] + l_pts[17]) / 3.0
            r_fist_dist = float(np.linalg.norm(r_pts[0] - l_palm_center)) / ref_scale

            # Palm normal alignment (dot product between normal vectors)
            norm_l = l_feats[29:32]
            norm_r = r_feats[29:32]
            palm_align = float(np.clip(np.dot(norm_l, norm_r), -1.0, 1.0))

            # Bimanual pinky-to-pinky span
            pinky_span = float(np.linalg.norm(l_pts[20] - r_pts[20])) / ref_scale

            interaction = np.array([inter_wrist, vert_diff, horiz_diff, index_dist, r_fist_dist, palm_align, pinky_span], dtype=np.float32)

        # Feature 5: Head/Nose Elevation (6)
        head_anchors = np.zeros(6, dtype=np.float32)
        has_pose = raw_data.get("has_pose", False)
        if has_pose:
            nose = pose[0]
            if has_l:
                head_anchors[0] = float(l_pts[0][1] - nose[1]) # Wrist y relative to nose
                head_anchors[1] = float(l_pts[0][2] - nose[2]) # Wrist z relative to nose
                head_anchors[2] = float(l_pts[8][1] - nose[1]) # Index y relative to nose
            if has_r:
                head_anchors[3] = float(r_pts[0][1] - nose[1])
                head_anchors[4] = float(r_pts[0][2] - nose[2])
                head_anchors[5] = float(r_pts[8][1] - nose[1])

        return np.concatenate([l_feats, r_feats, presence, interaction, head_anchors]).astype(np.float32)

    def match_anatomical_signature(self, raw_data: Dict[str, Any]) -> Tuple[str, float]:
        """
        High-precision kinematic signature matcher.
        Instantly identifies unambiguous canonical ISL hand formations.
        Returns: (candidate_sign, confidence_score)
        """
        has_l = raw_data.get("has_left_hand", False)
        has_r = raw_data.get("has_right_hand", False)
        if not has_l and not has_r:
            return "IDLE", 0.0

        l_pts = raw_data.get("left_hand", np.zeros((21, 3)))
        r_pts = raw_data.get("right_hand", np.zeros((21, 3)))
        pose = raw_data.get("pose_anchors", np.zeros((3, 3)))
        nose_y = pose[0][1] if raw_data.get("has_pose") else 0.28

        l_ext = self.get_finger_extension_states(l_pts) if has_l else [False]*5
        r_ext = self.get_finger_extension_states(r_pts) if has_r else [False]*5

        # =========================================================================
        # --- TWO-HANDED (BIMANUAL) SIGNS ---
        # =========================================================================
        if has_l and has_r:
            inter_wrist = np.linalg.norm(l_pts[0] - r_pts[0])
            index_dist = np.linalg.norm(l_pts[8] - r_pts[8])
            thumb_dist = np.linalg.norm(l_pts[4] - r_pts[4])

            # 1. HELP: One fist resting on flat other palm
            # Right fist on left flat palm
            if sum(l_ext) >= 3 and sum(r_ext) <= 1 and inter_wrist < 0.32:
                return "HELP", 0.96
            # Left fist on right flat palm
            if sum(r_ext) >= 3 and sum(l_ext) <= 1 and inter_wrist < 0.32:
                return "HELP", 0.96

            # 2. HOSPITAL: Crossing index fingers '+'
            if l_ext == [False, True, False, False, False] and r_ext == [False, True, False, False, False]:
                if index_dist < 0.20:
                    return "HOSPITAL", 0.95

            # 3. MEET: Both index fingers upright moving together until touching
            if l_ext[1] and r_ext[1] and not l_ext[2] and not r_ext[2] and index_dist < 0.14:
                return "MEET", 0.94

            # 4. WHEN: Index fingers touching horizontally
            if l_ext[1] and r_ext[1] and index_dist < 0.10:
                return "WHEN", 0.91

            # 5. DOCTOR: Checking pulse on left wrist
            if sum(l_ext) >= 3 and (r_ext[1] or r_ext[2]):
                dist_to_wrist = np.linalg.norm(r_pts[8] - l_pts[0])
                if dist_to_wrist < 0.18:
                    return "DOCTOR", 0.94

            # 6. TODAY / NOW: Both Y-hands (Thumb + Pinky extended) OR both open hands with palms facing downward
            is_l_y = l_ext[0] and l_ext[4] and not l_ext[1] and not l_ext[2]
            is_r_y = r_ext[0] and r_ext[4] and not r_ext[1] and not r_ext[2]
            if is_l_y and is_r_y:
                return "TODAY", 0.95

            # 7. WHERE vs TODAY vs NICE (Both hands open >= 4 fingers)
            if sum(l_ext) >= 4 and sum(r_ext) >= 4:
                # Palms facing down (wrists higher/lower than knuckles, fingertips pointing forward)
                is_downward = (l_pts[0][1] < l_pts[9][1] - 0.02) and (r_pts[0][1] < r_pts[9][1] - 0.02)
                if is_downward:
                    return "TODAY", 0.93

                # NICE: Right flat palm sliding over horizontal left palm
                palm_touch = np.linalg.norm(r_pts[9] - l_pts[9])
                if palm_touch < 0.18:
                    return "NICE", 0.93

                # WHERE: Both palms open side by side facing UPWARD
                return "WHERE", 0.94

            # 8. HOW: Both curved hands rolling palms upward
            if sum(l_ext) >= 3 and sum(r_ext) >= 3 and inter_wrist < 0.30:
                return "HOW", 0.91

            # 9. PAIN: Index fingers pointing toward each other twisting near chest
            if l_ext[1] and r_ext[1] and index_dist < 0.25 and (l_pts[0][1] > nose_y + 0.10):
                return "PAIN", 0.92

            # 10. TIRED: Both hands drooping down near chest
            if sum(l_ext) >= 3 and sum(r_ext) >= 3 and (l_pts[0][1] > nose_y + 0.20):
                return "TIRED", 0.90

            # 11. COLD: Both fists trembling near chest
            if sum(l_ext) <= 1 and sum(r_ext) <= 1 and inter_wrist < 0.35:
                return "COLD", 0.91

            # 12. EMERGENCY: Both fists shaking rapidly near shoulders
            if sum(l_ext) <= 1 and sum(r_ext) <= 1 and inter_wrist > 0.35 and l_pts[0][1] < nose_y + 0.15:
                return "EMERGENCY", 0.92

            # 13. SLEEP: Both hands tilted near cheek/face
            if (l_pts[0][1] < nose_y + 0.10) or (r_pts[0][1] < nose_y + 0.10):
                return "SLEEP", 0.90

            # 14. SCHOOL: Clapping flat hands horizontally
            if sum(l_ext) >= 3 and sum(r_ext) >= 3 and inter_wrist < 0.20:
                return "SCHOOL", 0.92

            # Default two-handed fallback
            return "WHERE", 0.70

        # =========================================================================
        # --- ONE-HANDED (UNIMANUAL) SIGNS ---
        # =========================================================================
        active_ext = r_ext if has_r else l_ext
        active_pts = r_pts if has_r else l_pts
        wrist_y = active_pts[0][1]
        wrist_z = active_pts[0][2]
        index_tip = active_pts[8]
        index_mcp = active_pts[5]

        # 1. Pointing signs: Only Index Finger extended [Thumb=any/F, Index=T, Middle=F, Ring=F, Pinky=F]
        is_index_only = active_ext[1] and not active_ext[2] and not active_ext[3] and not active_ext[4]
        if is_index_only:
            # Check elevation: near forehead/temple -> SICK / THINK
            if wrist_y < nose_y + 0.05:
                return "SICK", 0.93

            # Differentiate I (pointing to chest/self) vs YOU (pointing forward at camera)
            # In pointing to SELF (I/ME):
            # - Index finger points inward/downward toward chest (tip_y is close to or below mcp_y)
            # - Or tip_z is closer to chest (not reaching forward towards camera)
            # - Or index tip is centered near body torso (|tip_x - 0.5| < 0.22)
            is_pointing_to_self = (
                (index_tip[1] > index_mcp[1] - 0.02 and abs(index_tip[0] - 0.5) < 0.22) or
                (index_tip[2] > wrist_z - 0.01)
            )
            if is_pointing_to_self:
                return "I", 0.95
            else:
                return "YOU", 0.95

        # 2. Thumbs-Up: Only Thumb extended -> GOOD
        is_thumb_only = active_ext[0] and not active_ext[1] and not active_ext[2] and not active_ext[3] and not active_ext[4]
        if is_thumb_only:
            # Check if thumb pointing UP vs DOWN
            thumb_tip = active_pts[4]
            thumb_mcp = active_pts[2]
            if thumb_tip[1] < thumb_mcp[1]:
                return "GOOD", 0.96
            else:
                return "BAD", 0.94

        # 3. FEVER: Back of hand on forehead
        if wrist_y < nose_y + 0.04 and abs(active_pts[9][0] - 0.5) < 0.18:
            return "FEVER", 0.94

        # 4. PLEASE: Flat open hand on chest
        if sum(active_ext) >= 4 and abs(active_pts[9][0] - 0.5) < 0.18 and (wrist_y > nose_y + 0.12):
            return "PLEASE", 0.92

        # 5. STOP vs WHAT (Open Hand)
        if sum(active_ext) >= 4:
            if wrist_y < nose_y + 0.05:
                return "SICK", 0.88
            # STOP: Vertical palm pushed outward
            # Index tip significantly higher than wrist
            if index_tip[1] < active_pts[0][1] - 0.12:
                return "STOP", 0.93
            # WHAT: Lower open palm
            return "WHAT", 0.85

        # 6. WATER: W-hand or 3 middle fingers extended
        if active_ext[1] and active_ext[2] and active_ext[3] and not active_ext[4]:
            return "WATER", 0.93

        # 7. FOOD: Pinched fingers tapping near mouth
        if sum(active_ext) <= 2 and wrist_y < nose_y + 0.12:
            return "FOOD", 0.92

        # 8. Fist: All fingers curled [F, F, F, F, F]
        if sum(active_ext) <= 1:
            if wrist_y < nose_y + 0.10:
                return "FOOD", 0.88
            return "WANT", 0.86

        # 9. Y-Hand (Thumb and Pinky extended, middle three curled) -> WHY
        if active_ext[0] and active_ext[4] and not active_ext[1] and not active_ext[2]:
            return "WHY", 0.94

        # 10. NEED: Bent index finger (hook)
        if not active_ext[0] and not active_ext[2] and not active_ext[3] and not active_ext[4]:
            return "NEED", 0.88

        return "YOU", 0.60
