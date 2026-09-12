"""Speech-to-Text conversion module."""
import speech_recognition as sr
from typing import Optional
from config.settings import SPEECH_ENERGY_THRESHOLD, SPEECH_PAUSE_THRESHOLD, DEBUG


class SpeechToTextEngine:
    """Manages audio capture and transcription."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200  # Highly sensitive to catch normal laptop voice
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.6  # Fast 0.6s response after speaking
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.4

    def calibrate_noise(self, source, duration: float = 0.5):
        """Calibrate microphone for background ambient noise."""
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            # Ensure energy threshold doesn't get set too high after calibration
            if self.recognizer.energy_threshold > 800:
                self.recognizer.energy_threshold = 300
        except Exception as e:
            if DEBUG:
                print(f"[STT Calibrate Warning]: {e}")

    def transcribe(self, audio: sr.AudioData) -> Optional[str]:
        """Convert captured AudioData to text using Google Speech Recognition."""
        try:
            text = self.recognizer.recognize_google(audio)
            return text.strip()
        except sr.UnknownValueError:
            # Audio was unintelligible / silence
            return None
        except sr.RequestError as e:
            if DEBUG:
                print(f"[STT Network Error]: Could not request results from Speech Recognition service; {e}")
            return None
        except Exception as e:
            if DEBUG:
                print(f"[STT Unexpected Error]: {e}")
            return None


# Singleton instance
stt_engine = SpeechToTextEngine()
