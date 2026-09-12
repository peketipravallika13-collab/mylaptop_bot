"""Text-to-Speech engine for voice responses."""
import threading
import queue
import pyttsx3
from config.settings import VOICE_RATE, VOICE_VOLUME, VOICE_GENDER, DEBUG


class TextToSpeechEngine:
    """Thread-safe non-blocking Text-to-Speech synthesizer."""

    def __init__(self):
        self._speech_queue = queue.Queue()
        self._is_running = True
        self._worker_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        self._worker_thread.start()

    def _init_engine(self):
        """Initialize engine inside the worker thread for COM compatibility on Windows."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", VOICE_RATE)
            engine.setProperty("volume", VOICE_VOLUME)

            voices = engine.getProperty("voices")
            if voices:
                selected_voice = voices[0].id
                for v in voices:
                    if VOICE_GENDER.lower() in v.name.lower():
                        selected_voice = v.id
                        break
                engine.setProperty("voice", selected_voice)
            return engine
        except Exception as e:
            if DEBUG:
                print(f"[TTS Error] Could not initialize engine: {e}")
            return None

    def _process_speech_queue(self):
        engine = self._init_engine()
        while self._is_running:
            try:
                text = self._speech_queue.get(timeout=1.0)
                if text is None:
                    break
                if DEBUG:
                    print(f"[TTS Speaking]: {text}")
                
                if engine:
                    engine.say(text)
                    engine.runAndWait()
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if DEBUG:
                    print(f"[TTS Error during speak]: {e}")
                # Reinitialize engine if COM failed
                engine = self._init_engine()

    def speak(self, text: str):
        """Queue text to be spoken non-blockingly."""
        if not text:
            return
        self._speech_queue.put(text)

    def stop(self):
        """Stop TTS worker."""
        self._is_running = False
        self._speech_queue.put(None)


# Singleton instance
tts_engine = TextToSpeechEngine()
