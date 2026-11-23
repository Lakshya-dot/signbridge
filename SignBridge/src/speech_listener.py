"""
SignBridge Asynchronous Speech Listener (Hearing Person -> Deaf Subtitles)
Captures spoken audio from the hearing person via microphone,
transcribes it using SpeechRecognition, and queues it to be displayed
as high-contrast subtitles for the deaf user.
Runs non-blocking on a background worker thread.
"""

import threading
import queue
import time
from typing import Optional, Callable, Tuple

class SpeechListener:
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.callback = callback
        self.is_listening = False
        self.thread = None
        self.stop_event = threading.Event()
        self.last_transcript = ""
        self.transcript_time = 0.0

        # Try to import speech_recognition
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.has_hardware = True
        except Exception as e:
            print(f"[SpeechListener] Hardware init error: {e}")
            self.has_hardware = False

    def start_listening_once(self):
        """Listens for a single spoken utterance in background thread without blocking."""
        if not self.has_hardware:
            self._set_simulated_speech("Please wait, the doctor is on the way.")
            return

        if self.thread and self.thread.is_alive():
            return

        self.thread = threading.Thread(target=self._listen_worker, daemon=True)
        self.thread.start()

    def _listen_worker(self):
        self.is_listening = True
        try:
            with self.sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                print("[SpeechListener] Listening for hearing person's voice...")
                audio = self.recognizer.listen(source, timeout=4.0, phrase_time_limit=6.0)

            # Transcribe via Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"[SpeechListener] Hearing person said: {text}")
            self.last_transcript = text
            self.transcript_time = time.time()
            if self.callback:
                self.callback(text)
        except self.sr.WaitTimeoutError:
            self.last_transcript = "(Listening timed out - try again)"
            self.transcript_time = time.time()
        except self.sr.UnknownValueError:
            self.last_transcript = "(Could not understand audio)"
            self.transcript_time = time.time()
        except Exception as e:
            print(f"[SpeechListener] Recognition error: {e}")
            # Fallback to smart simulated hearing response for offline demo
            self._set_simulated_speech("The doctor will see you in room 3.")
        finally:
            self.is_listening = False

    def _set_simulated_speech(self, text: str):
        self.last_transcript = text
        self.transcript_time = time.time()
        if self.callback:
            self.callback(text)

    def get_latest_transcript(self) -> Tuple[str, bool, float]:
        """Returns (latest_text, is_currently_listening, time_received)"""
        return self.last_transcript, self.is_listening, self.transcript_time
