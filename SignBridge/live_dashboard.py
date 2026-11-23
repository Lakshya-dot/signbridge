"""
SignBridge Interactive Live Recognition Dashboard (v3.5 - Bidirectional Tele-Communicator)
Full-Featured Assistive Communication System for Deaf & Hard-of-Hearing Individuals:
- Direction 1 (Deaf -> Hearing): MediaPipe hand tracking -> 89-D invariant features -> 
  Random Forest / SVM classifier -> Hold-to-commit debouncing -> ISL-to-English grammar synthesis ->
  pyttsx3 spoken speech output.
- Direction 2 (Hearing -> Deaf): Background speech recognition listener capturing spoken audio
  from hearing individuals -> Large, high-contrast visual captions on HUD for deaf users.
- Multi-Lingual Regional Translation: Live translation into English, Hindi, Telugu, and Tamil.
- Emergency Clinical Intake Logger: Instant timestamped medical dialogue and symptom export ([E]).
- On-Screen Live Gesture Cheatsheet ([G]): Toggleable visual gesture prompt overlay.
- Interactive controls: [SPACE] Speak | [R] Listen Voice | [L] Language | [E] Export | [BACKSPACE] Undo
"""

import os
import sys
import time
import json
import joblib
import cv2
import numpy as np
from collections import deque, Counter
from datetime import datetime

from SignBridge.src.landmark_extractor import LandmarkExtractor
from SignBridge.src.feature_engine import FeatureEngine
from SignBridge.src.grammar_engine import ISLGrammarEngine
from SignBridge.src.tts_speaker import TextToSpeechSpeaker
from SignBridge.src.speech_listener import SpeechListener

class SignBridgeDashboard:
    def __init__(self, models_dir: str = "SignBridge/models", confidence_threshold: float = 0.50):
        self.models_dir = models_dir
        self.tau = confidence_threshold
        
        # Load Classes and Scaler
        classes_path = os.path.join(models_dir, "classes.json")
        scaler_path = os.path.join(models_dir, "scaler.joblib")
        rf_path = os.path.join(models_dir, "rf_model.joblib")
        svm_path = os.path.join(models_dir, "svm_model.joblib")

        if not os.path.exists(classes_path) or not os.path.exists(rf_path):
            raise FileNotFoundError(f"Model files not found in {models_dir}. Please train models first!")

        with open(classes_path, "r") as f:
            self.classes = json.load(f)
        
        self.scaler = joblib.load(scaler_path)
        self.rf_model = joblib.load(rf_path)
        self.svm_model = joblib.load(svm_path) if os.path.exists(svm_path) else self.rf_model
        
        self.active_model_name = "Random Forest"
        self.active_model = self.rf_model

        # Core Engines
        self.extractor = LandmarkExtractor(min_detection_confidence=0.45, min_tracking_confidence=0.45)
        self.feature_engine = FeatureEngine()
        self.grammar_engine = ISLGrammarEngine()
        self.tts = TextToSpeechSpeaker(rate=145)
        self.speech_listener = SpeechListener()

        # Multi-Lingual Regional Language State
        self.languages = ["ENGLISH", "HINDI", "TELUGU", "TAMIL"]
        self.lang_idx = 0
        self.current_lang = "ENGLISH"

        # Application Modes (Translate vs Educational ISL Tutor)
        self.mode = "TRANSLATE"
        self.tutor_targets = ["YOU", "GOOD", "HELP", "WHERE", "HOSPITAL", "SICK", "FEVER", "TODAY", "THANK YOU"]
        self.tutor_instructions = {
            "YOU": "Point your RIGHT index finger forward at the camera",
            "GOOD": "Show a clear THUMBS-UP at chest level",
            "HELP": "Rest your RIGHT fist on top of flat LEFT palm",
            "WHERE": "Raise BOTH hands with open palms facing UP side-by-side",
            "HOSPITAL": "Cross both index fingers into a PLUS sign (+)",
            "SICK": "Touch your forehead / temple with your right hand",
            "FEVER": "Place the back of your hand on your forehead",
            "TODAY": "Form 'Y' hands (thumb+pinky) or drop palms low near chest",
            "THANK YOU": "Touch flat hand to chin and move forward smoothly"
        }
        self.tutor_idx = 0
        self.tutor_score = 0
        self.tutor_success_time = 0.0

        # Sequence Buffers and State
        self.frame_buffer = deque(maxlen=7)
        self.gloss_sequence = []
        self.english_translation = "Ready. Begin signing..."
        self.regional_translation = ""
        self.current_rule = "Awaiting input"
        
        # Smart Hold-to-Commit & Anti-Spam Machine
        self.min_hold_frames = 10        # Require ~0.35s steady hold to lock
        self.sign_hold_frames = 0
        self.current_holding_sign = None
        self.locked_sign = None
        self.locked_display_time = 0.0
        self.cooldown_frames = 0         # Post-commit refractory period (ignores transitions)
        self.post_commit_cooldown = 22   # ~0.75s cooldown

        # Hand presence memory
        self.recent_two_hands = 0

        # Hearing Person Subtitles State (Direction 2: Hearing -> Deaf)
        self.hearing_text = "Press [R] to listen to hearing person's reply"
        self.hearing_time = 0.0
        self.is_listening = False

        # Session Transcript & Triage Export
        self.session_log = []
        self.export_message = ""
        self.export_display_time = 0.0
        self.show_cheatsheet = False

        # Timing and Auto-Speech
        self.last_sign_time = time.time()
        self.idle_timeout = 2.2          # Auto-speak after 2.2s of silence
        self.auto_speak_enabled = True
        self.show_landmarks = True
        self.has_spoken_current = False

        # FPS metrics
        self.prev_time = time.time()
        self.fps = 0.0
        self.top5_predictions = []

    def set_language(self, lang_name: str):
        lang_name = lang_name.upper().strip()
        if lang_name in self.languages:
            self.current_lang = lang_name
            self.lang_idx = self.languages.index(lang_name)
            self._update_translations()
            self.tts.speak(f"Language set to {self.current_lang.capitalize()}")

    def get_telemetry(self) -> dict:
        return {
            "fps": round(self.fps, 1),
            "active_model": self.active_model_name,
            "current_lang": self.current_lang,
            "mode": self.mode,
            "gloss_sequence": list(self.gloss_sequence),
            "english_translation": self.english_translation,
            "regional_translation": self.regional_translation,
            "current_rule": self.current_rule,
            "hearing_text": self.hearing_text,
            "is_listening": self.is_listening,
            "hold_pct": int(min(1.0, self.sign_hold_frames / float(self.min_hold_frames)) * 100),
            "in_cooldown": self.cooldown_frames > 0,
            "current_holding_sign": self.current_holding_sign or "IDLE",
            "active_pred_sign": getattr(self, "active_display_status", "IDLE"),
            "confidence": round(getattr(self, "active_confidence", 0.0) * 100, 1),
            "has_left_hand": getattr(self, "has_left_hand", False),
            "has_right_hand": getattr(self, "has_right_hand", False),
            "top5": getattr(self, "top5_predictions", []),
            "tutor": {
                "target": self.tutor_targets[self.tutor_idx] if self.mode == "TUTOR" else "",
                "instruction": self.tutor_instructions.get(self.tutor_targets[self.tutor_idx], "") if self.mode == "TUTOR" else "",
                "score": self.tutor_score,
                "is_success": (time.time() - self.tutor_success_time) < 1.5
            },
            "recent_log": self.session_log[-6:] if self.session_log else []
        }

    def toggle_model(self):
        if self.active_model_name == "Random Forest":
            self.active_model_name = "SVM (RBF)"
            self.active_model = self.svm_model
        else:
            self.active_model_name = "Random Forest"
            self.active_model = self.rf_model

    def toggle_language(self):
        self.lang_idx = (self.lang_idx + 1) % len(self.languages)
        self.current_lang = self.languages[self.lang_idx]
        self._update_translations()
        self.tts.speak(f"Language set to {self.current_lang.capitalize()}")

    def toggle_mode(self):
        if self.mode == "TRANSLATE":
            self.mode = "TUTOR"
            self.tts.speak("ISL Tutor Mode activated.")
        else:
            self.mode = "TRANSLATE"
            self.tts.speak("Translator Mode activated.")
        self.reset_sentence()

    def reset_sentence(self):
        self.gloss_sequence.clear()
        self.english_translation = "Ready. Begin signing..."
        self.regional_translation = ""
        self.current_rule = "Buffer cleared"
        self.current_holding_sign = None
        self.sign_hold_frames = 0
        self.locked_sign = None
        self.cooldown_frames = 0
        self.has_spoken_current = False

    def undo_last_sign(self):
        """Removes the most recent committed sign from the sequence."""
        if self.gloss_sequence:
            popped = self.gloss_sequence.pop()
            if self.gloss_sequence:
                self._update_translations()
            else:
                self.english_translation = "Ready. Begin signing..."
                self.regional_translation = ""
                self.current_rule = "Buffer empty"
            self.current_holding_sign = None
            self.sign_hold_frames = 0
            self.locked_sign = None
            self.cooldown_frames = 0
            self.has_spoken_current = False
            return popped
        return None

    def start_listening_to_hearing(self):
        """Starts asynchronous microphone listening for the hearing person's response."""
        self.speech_listener.start_listening_once()

    def export_session_log(self):
        """Exports the complete dialogue transcript and clinical triage intake summary."""
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_filename = "SignBridge_Session_Log.txt"
        
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"SIGNBRIDGE ASSISTIVE SESSION REPORT\n")
            f.write(f"Timestamp: {timestamp_str}\n")
            f.write(f"Active Language: {self.current_lang}\n")
            f.write(f"Active Classifier: {self.active_model_name}\n")
            f.write(f"{'-'*70}\n")
            f.write("CONVERSATION LOG (BIDIRECTIONAL):\n")
            for entry in self.session_log:
                f.write(f"  [{entry['time']}] {entry['speaker']}: {entry['text']}\n")
            if self.english_translation and self.english_translation != "Ready. Begin signing...":
                f.write(f"  [{timestamp_str}] DEAF SIGNER (Current): {self.english_translation}\n")
                if self.regional_translation:
                    f.write(f"    Regional ({self.current_lang}): {self.regional_translation}\n")
            f.write(f"{'='*70}\n\n")

        self.export_message = f"LOG SAVED: {log_filename}"
        self.export_display_time = time.time()
        self.tts.speak("Session log exported successfully.")

    def _update_translations(self):
        if self.gloss_sequence:
            self.english_translation, self.current_rule = self.grammar_engine.translate(self.gloss_sequence)
            self.regional_translation = self.grammar_engine.get_regional_translation(self.english_translation, self.current_lang)
        else:
            self.english_translation = "Ready. Begin signing..."
            self.regional_translation = ""

    def speak_current(self):
        if self.gloss_sequence and self.english_translation:
            # If regional language selected, speak regional or English
            text_to_speak = self.english_translation
            self.tts.speak(text_to_speak, deduplicate=False)
            self.has_spoken_current = True
            
            # Log to session
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.session_log.append({
                "time": timestamp,
                "speaker": "DEAF SIGNER",
                "text": f"{self.english_translation} (Glosses: {' -> '.join(self.gloss_sequence)})"
            })

    def process_frame(self, frame: np.ndarray, render_opencv_hud: bool = True) -> np.ndarray:
        # FPS calculation
        curr_time = time.time()
        dt = curr_time - self.prev_time
        self.prev_time = curr_time
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)

        # Check for incoming speech recognition from hearing person
        h_text, h_listening, h_time = self.speech_listener.get_latest_transcript()
        self.is_listening = h_listening
        if h_text and h_time > self.hearing_time:
            self.hearing_text = h_text
            self.hearing_time = h_time
            # Log hearing person's speech
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.session_log.append({
                "time": timestamp,
                "speaker": "HEARING PERSON",
                "text": h_text
            })

        h, w, _ = frame.shape
        data = self.extractor.process_frame(frame)

        if self.show_landmarks:
            display_frame = self.extractor.draw_landmarks(frame.copy(), data)
        else:
            display_frame = frame.copy()

        has_l = data["has_left_hand"]
        has_r = data["has_right_hand"]
        has_hands = has_l or has_r

        # Track bimanual grace memory
        if has_l and has_r:
            self.recent_two_hands = 15
        elif self.recent_two_hands > 0:
            self.recent_two_hands -= 1

        current_pred_sign = "IDLE"
        display_status = "IDLE"
        confidence = 0.0

        if has_hands:
            # 1. Kinematic signature match
            kin_sign, kin_conf = self.feature_engine.match_anatomical_signature(data)

            # 2. Machine Learning model prediction
            feat_vec = self.feature_engine.extract_full_features(data).reshape(1, -1)
            feat_scaled = self.scaler.transform(feat_vec)
            probs = self.active_model.predict_proba(feat_scaled)[0]
            ml_idx = int(np.argmax(probs))
            ml_conf = float(probs[ml_idx])
            ml_sign = self.classes[ml_idx]

            # Top 5 candidate probabilities for real-time telemetry HUD
            top_indices = np.argsort(probs)[::-1][:5]
            self.top5_predictions = [
                {"sign": self.classes[i], "prob": round(float(probs[i]), 3)}
                for i in top_indices
            ]

            # Bimanual Disambiguation Guard:
            if kin_sign == "WHAT" and self.recent_two_hands > 0:
                kin_conf = 0.60

            # Ensemble decision:
            if kin_conf >= 0.85:
                best_sign = kin_sign
                confidence = kin_conf
            elif ml_conf >= self.tau and ml_sign != "IDLE":
                best_sign = ml_sign
                confidence = ml_conf
            else:
                best_sign = kin_sign if kin_conf > ml_conf else ml_sign
                confidence = max(kin_conf, ml_conf)

            if confidence >= self.tau and best_sign != "IDLE":
                current_pred_sign = best_sign
                display_status = best_sign
            else:
                current_pred_sign = "UNCERTAIN"
                display_status = f"{best_sign}?" if best_sign != "IDLE" else "UNCERTAIN"
        else:
            current_pred_sign = "IDLE"
            display_status = "IDLE"
            self.top5_predictions = []

        # Cooldown & Hold-to-Commit Machine
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
            self.sign_hold_frames = 0
            self.current_holding_sign = None
        else:
            if current_pred_sign not in ["IDLE", "UNCERTAIN"] and confidence >= self.tau:
                if current_pred_sign == self.current_holding_sign:
                    self.sign_hold_frames += 1
                else:
                    self.current_holding_sign = current_pred_sign
                    self.sign_hold_frames = 1

                # Check if hold duration reached (10 frames ~ 0.35s)
                if self.sign_hold_frames >= self.min_hold_frames:
                    committed_sign = self.current_holding_sign

                    if self.mode == "TUTOR":
                        target = self.tutor_targets[self.tutor_idx]
                        if committed_sign == target:
                            self.tutor_score += 10
                            self.tts.speak("Correct! Excellent job.")
                            self.tutor_success_time = time.time()
                            self.tutor_idx = (self.tutor_idx + 1) % len(self.tutor_targets)
                            self.locked_sign = committed_sign
                            self.locked_display_time = time.time()
                            self.cooldown_frames = self.post_commit_cooldown
                            self.sign_hold_frames = 0
                    else:
                        # Translate Mode Commit
                        if not self.gloss_sequence or self.gloss_sequence[-1] != committed_sign:
                            self.gloss_sequence.append(committed_sign)
                            self._update_translations()
                            self.last_sign_time = time.time()
                            self.has_spoken_current = False

                        self.locked_sign = committed_sign
                        self.locked_display_time = time.time()
                        self.cooldown_frames = self.post_commit_cooldown
                        self.sign_hold_frames = 0
            else:
                if current_pred_sign == "IDLE":
                    self.sign_hold_frames = max(0, self.sign_hold_frames - 2)

        # Auto-speak after pause in Translate mode
        if self.mode == "TRANSLATE" and self.auto_speak_enabled and self.gloss_sequence and not self.has_spoken_current:
            if (time.time() - self.last_sign_time) > self.idle_timeout and self.cooldown_frames == 0:
                self.speak_current()

        # Save telemetry state
        self.active_display_status = display_status
        self.active_confidence = float(confidence)
        self.has_left_hand = has_l
        self.has_right_hand = has_r

        # Render Modern HUD if requested (OpenCV Desktop window)
        if render_opencv_hud:
            self._render_hud(display_frame, current_pred_sign, display_status, confidence, data)
        return display_frame

    def _render_hud(self, img: np.ndarray, pred_sign: str, display_status: str, conf: float, raw_data: dict):
        h, w, _ = img.shape

        # 1. Top Header Banner
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, 65), (15, 18, 25), -1)
        cv2.addWeighted(overlay, 0.88, img, 0.12, 0, img)

        cv2.putText(img, "SignBridge Tele-Communicator", (20, 36), cv2.FONT_HERSHEY_DUPLEX, 0.85, (0, 220, 255), 2)
        cv2.putText(img, "(Amrita RAI · Bidirectional Bridge)", (380, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (180, 190, 200), 1)

        # Status pills: Mode, Language, Model, FPS
        mode_str = "MODE: TUTOR [T]" if self.mode == "TUTOR" else "MODE: TRANSLATOR [T]"
        mode_color = (0, 255, 120) if self.mode == "TUTOR" else (0, 200, 255)
        cv2.putText(img, mode_str, (w - 580, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.44, mode_color, 2)

        lang_str = f"LANG: {self.current_lang} [L]"
        cv2.putText(img, lang_str, (w - 390, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 230, 255), 1)
        
        model_str = f"Model: {self.active_model_name} [M]"
        cv2.putText(img, model_str, (w - 230, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (255, 255, 255), 1)

        fps_str = f"FPS: {self.fps:.0f}"
        cv2.putText(img, fps_str, (w - 70, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 255), 1)

        # 2. Left Detection Info Card
        card_w, card_h = 320, 185
        cv2.rectangle(img, (20, 80), (20 + card_w, 80 + card_h), (25, 28, 35), -1)
        cv2.rectangle(img, (20, 80), (20 + card_w, 80 + card_h), (60, 70, 85), 1)

        in_cooldown = self.cooldown_frames > 0

        if self.mode == "TUTOR":
            target = self.tutor_targets[self.tutor_idx]
            cv2.putText(img, f"CHALLENGE TARGET: {target}", (35, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 230, 255), 1)
            is_matching = (pred_sign == target and conf >= self.tau)
            if is_matching:
                sign_color = (0, 255, 120)
                badge_text = f"HOLD: {self.sign_hold_frames}/{self.min_hold_frames}"
            elif pred_sign not in ["IDLE", "UNCERTAIN"]:
                sign_color = (0, 165, 255)
                badge_text = f"Saw: {pred_sign}"
            else:
                sign_color = (160, 160, 160)
                badge_text = "Awaiting Hand"
        else:
            if in_cooldown:
                cv2.putText(img, "LOCKED & COOLDOWN", (35, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 150), 1)
                badge_text = f"LOCKED: {self.locked_sign}"
                sign_color = (0, 255, 120)
            else:
                cv2.putText(img, "ACTIVE DETECTION", (35, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 175), 1)
                if pred_sign not in ["IDLE", "UNCERTAIN"]:
                    sign_color = (0, 255, 120)
                    badge_text = pred_sign
                elif display_status != "IDLE":
                    sign_color = (0, 165, 255)
                    badge_text = display_status
                else:
                    sign_color = (160, 160, 160)
                    badge_text = "IDLE"

        cv2.putText(img, badge_text, (35, 142), cv2.FONT_HERSHEY_DUPLEX, 0.95, sign_color, 2)

        # Hold-to-Commit Progress Bar
        bar_x, bar_y, bar_w, bar_h = 35, 160, 250, 12
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 55, 65), -1)
        
        if in_cooldown:
            cool_ratio = self.cooldown_frames / float(self.post_commit_cooldown)
            fill_w = int(bar_w * cool_ratio)
            cv2.rectangle(img, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (0, 200, 255), -1)
            cv2.putText(img, "Transition Cooldown (Hold Steady)", (35, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 220, 255), 1)
        else:
            hold_ratio = min(1.0, self.sign_hold_frames / float(self.min_hold_frames))
            fill_w = int(bar_w * hold_ratio)
            fill_color = (0, 255, 120) if hold_ratio >= 0.8 else (0, 200, 255)
            cv2.rectangle(img, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), fill_color, -1)
            hold_pct = int(hold_ratio * 100)
            cv2.putText(img, f"Hold to Commit: {hold_pct}% | Conf: {conf*100:.0f}%", (35, 190),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 200, 200), 1)

        l_flag = "Left: YES" if raw_data.get("has_left_hand") else "Left: NO"
        r_flag = "Right: YES" if raw_data.get("has_right_hand") else "Right: NO"
        cv2.putText(img, f"{l_flag} | {r_flag}", (35, 212), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (170, 175, 185), 1)

        # 3. BIDIRECTIONAL HEARING PERSON SUBTITLES CARD (Hearing -> Deaf)
        h_card_x, h_card_y, h_card_w, h_card_h = 360, 80, 560, 75
        cv2.rectangle(img, (h_card_x, h_card_y), (h_card_x + h_card_w, h_card_y + h_card_h), (25, 28, 42), -1)
        border_c = (0, 255, 255) if self.is_listening else (70, 80, 100)
        cv2.rectangle(img, (h_card_x, h_card_y), (h_card_x + h_card_w, h_card_y + h_card_h), border_c, 1)

        mic_label = "MIC LISTENING... (Hearing person speak)" if self.is_listening else "HEARING PERSON SPEECH [Tap 'R' to Listen]"
        mic_color = (0, 255, 255) if self.is_listening else (0, 220, 255)
        cv2.putText(img, mic_label, (h_card_x + 15, h_card_y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.44, mic_color, 1)
        
        # Transcript of what hearing person said
        cv2.putText(img, f"\"{self.hearing_text}\"", (h_card_x + 15, h_card_y + 54),
                    cv2.FONT_HERSHEY_DUPLEX, 0.58, (255, 255, 255), 1)

        # Export Banner notification
        if (time.time() - self.export_display_time) < 2.5 and self.export_message:
            cv2.rectangle(img, (w - 380, 80), (w - 20, 125), (20, 80, 40), -1)
            cv2.rectangle(img, (w - 380, 80), (w - 20, 125), (0, 255, 120), 2)
            cv2.putText(img, self.export_message, (w - 365, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

        # 4. Bottom Subtitle & Sentence Banner
        banner_h = 150
        cv2.rectangle(img, (20, h - banner_h - 15), (w - 20, h - 15), (20, 22, 28), -1)
        border_col = (0, 255, 120) if self.mode == "TUTOR" else (0, 200, 255)
        cv2.rectangle(img, (20, h - banner_h - 15), (w - 20, h - 15), border_col, 2)

        if self.mode == "TUTOR":
            target = self.tutor_targets[self.tutor_idx]
            instr = self.tutor_instructions.get(target, "")
            is_recent = (time.time() - self.tutor_success_time) < 1.4

            cv2.putText(img, f"ISL EDUCATIONAL TUTOR  |  Score: {self.tutor_score} pts",
                        (35, h - banner_h + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 120), 2)
            if is_recent:
                cv2.putText(img, "CORRECT! EXCELLENT JOB!", (35, h - banner_h + 75),
                            cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 120), 2)
            else:
                cv2.putText(img, f"CHALLENGE: Sign \"{target}\"", (35, h - banner_h + 68),
                            cv2.FONT_HERSHEY_DUPLEX, 0.90, (0, 230, 255), 2)
                cv2.putText(img, f"Instruction: {instr}", (35, h - banner_h + 105),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)

            cv2.putText(img, "[T] Return to Translator", (w - 280, h - banner_h + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (180, 180, 180), 1)
        else:
            # Gloss tokens stream
            gloss_text = " -> ".join(self.gloss_sequence) if self.gloss_sequence else "[ Awaiting Signs ]"
            cv2.putText(img, "GLOSS STREAM:", (35, h - banner_h + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 200, 255), 1)
            cv2.putText(img, gloss_text, (160, h - banner_h + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2)

            # English translation
            cv2.putText(img, "ENGLISH:", (35, h - banner_h + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 150), 1)
            cv2.putText(img, f"\"{self.english_translation}\"", (125, h - banner_h + 54),
                        cv2.FONT_HERSHEY_DUPLEX, 0.78, (0, 255, 180), 2)

            # Regional translation (Hindi / Telugu / Tamil)
            if self.regional_translation and self.current_lang != "ENGLISH":
                cv2.putText(img, f"{self.current_lang}:", (35, h - banner_h + 88), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 220, 255), 1)
                cv2.putText(img, f"\"{self.regional_translation}\"", (125, h - banner_h + 90),
                            cv2.FONT_HERSHEY_DUPLEX, 0.65, (240, 245, 255), 1)
            else:
                cv2.putText(img, f"Grammar Rule: {self.current_rule}", (35, h - banner_h + 88),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (160, 165, 175), 1)

        # Controls hint at bottom of banner
        hints = "[SPACE] Speak | [R] Listen Voice | [L] Language | [E] Export Log | [BACKSPACE] Undo | [C] Clear | [T] Mode | [Q] Quit"
        cv2.putText(img, hints, (35, h - banner_h + 130), cv2.FONT_HERSHEY_SIMPLEX, 0.41, (200, 200, 200), 1)


def launch_dashboard():
    dashboard = SignBridgeDashboard()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open default camera (index 0).")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow("SignBridge - Indian Sign Language Translator", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("SignBridge - Indian Sign Language Translator", 1280, 720)

    print("\n" + "="*70)
    print("  SignBridge v3.5: Bidirectional Assistive Communication Dashboard")
    print("="*70)
    print("Controls:")
    print("  [SPACE] / [S]   - Speak current sentence aloud (TTS)")
    print("  [R]             - Listen to hearing person's spoken response (STT)")
    print("  [L]             - Toggle Regional Language (English <-> Hindi <-> Telugu <-> Tamil)")
    print("  [E]             - Export clinical session transcript & triage log")
    print("  [BACKSPACE]/[B] - Undo / Delete last recognized sign")
    print("  [C]             - Clear full recognized sentence & reset")
    print("  [T]             - Toggle Modes (Translator <-> Educational Tutor)")
    print("  [M]             - Switch active ML Model (Random Forest <-> SVM)")
    print("  [V]             - Toggle Auto-Speech Mode")
    print("  [H]             - Toggle Skeleton Overlay on/off")
    print("  [Q] / [ESC]     - Quit Application")
    print("="*70 + "\n")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to read webcam frame.")
                break

            frame = cv2.flip(frame, 1) # Mirror view
            annotated = dashboard.process_frame(frame)
            cv2.imshow("SignBridge - Indian Sign Language Translator", annotated)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord(' ') or key == ord('s'):
                dashboard.speak_current()
            elif key == ord('r'):
                dashboard.start_listening_to_hearing()
            elif key == ord('l'):
                dashboard.toggle_language()
            elif key == ord('e'):
                dashboard.export_session_log()
            elif key == ord('c'):
                dashboard.reset_sentence()
            elif key == ord('b') or key == 8:
                dashboard.undo_last_sign()
            elif key == ord('m'):
                dashboard.toggle_model()
            elif key == ord('t'):
                dashboard.toggle_mode()
            elif key == ord('v'):
                dashboard.auto_speak_enabled = not dashboard.auto_speak_enabled
            elif key == ord('h'):
                dashboard.show_landmarks = not dashboard.show_landmarks

    finally:
        cap.release()
        cv2.destroyAllWindows()
        dashboard.extractor.close()
        dashboard.tts.shutdown()
        print("SignBridge live dashboard stopped cleanly.")


if __name__ == "__main__":
    launch_dashboard()
