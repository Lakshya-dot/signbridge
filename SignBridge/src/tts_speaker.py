"""
SignBridge Threaded Text-to-Speech (TTS) Engine
Uses pyttsx3 in an asynchronous worker thread so the camera feed never freezes during audio synthesis.
"""

import threading
import queue
import time
import logging

class TextToSpeechSpeaker:
    def __init__(self, rate: int = 150, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.last_spoken_text = ""
        self.worker_thread = threading.Thread(target=self._run_worker, daemon=True)
        self.worker_thread.start()

    def _run_worker(self):
        """Worker loop that initializes pyttsx3 within its own thread context."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)
            
            # Select clear English voice if available
            voices = engine.getProperty('voices')
            for v in voices:
                if "english" in v.name.lower() or "david" in v.name.lower() or "zira" in v.name.lower():
                    engine.setProperty('voice', v.id)
                    break
        except Exception as e:
            logging.warning(f"pyttsx3 initialization notice: {e}. Voice output will run in fallback print mode.")
            engine = None

        while not self.stop_event.is_set():
            try:
                text = self.queue.get(timeout=0.2)
                if text is None:
                    break
                if engine:
                    engine.say(text)
                    engine.runAndWait()
                else:
                    print(f"[AUDIO SIMULATION]: \"{text}\"")
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as ex:
                logging.error(f"TTS Speech error: {ex}")

    def speak(self, text: str, deduplicate: bool = True):
        """Enqueue text to be spoken asynchronously."""
        if not text or not text.strip():
            return
        clean_text = text.strip()
        if deduplicate and clean_text == self.last_spoken_text:
            return
        self.last_spoken_text = clean_text
        self.queue.put(clean_text)

    def shutdown(self):
        self.stop_event.set()
        self.queue.put(None)
        self.worker_thread.join(timeout=1.0)


if __name__ == "__main__":
    speaker = TextToSpeechSpeaker()
    print("Testing speech engine...")
    speaker.speak("SignBridge initialized. Indian Sign Language translator is ready.")
    time.sleep(3)
    speaker.shutdown()
    print("Speech test completed.")
