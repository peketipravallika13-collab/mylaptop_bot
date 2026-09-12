"""Background Microphone Voice Listener."""
import threading
import time
import speech_recognition as sr
from typing import Callable, Optional
from voice.speech_to_text import stt_engine
from config.settings import DEBUG


class VoiceListener:
    """Controls continuous and on-demand voice listening."""

    def __init__(self):
        self.is_active = False
        self._stop_event = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None
        self._on_command_callback: Optional[Callable[[str], None]] = None
        self._on_status_callback: Optional[Callable[[str], None]] = None

    def start_listening(
        self,
        on_command: Callable[[str], None],
        on_status: Optional[Callable[[str], None]] = None
    ):
        """Start background microphone loop."""
        if self.is_active:
            return
        
        self.is_active = True
        self._stop_event.clear()
        self._on_command_callback = on_command
        self._on_status_callback = on_status

        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        
        if self._on_status_callback:
            self._on_status_callback("LISTENING")

    def stop_listening(self):
        """Stop voice listening."""
        if not self.is_active:
            return
        
        self.is_active = False
        self._stop_event.set()
        
        if self._on_status_callback:
            self._on_status_callback("IDLE")

    def toggle(self, on_command: Callable[[str], None], on_status: Optional[Callable[[str], None]] = None):
        """Toggle listening state."""
        if self.is_active:
            self.stop_listening()
        else:
            self.start_listening(on_command, on_status)

    def _listen_loop(self):
        """Internal audio listening loop with ambient adjustment."""
        try:
            with sr.Microphone() as source:
                if DEBUG:
                    print("[Listener] Calibrating microphone for ambient noise...")
                if self._on_status_callback:
                    self._on_status_callback("CALIBRATING")
                stt_engine.calibrate_noise(source, duration=0.8)
                
                if self._on_status_callback:
                    self._on_status_callback("LISTENING")

                while not self._stop_event.is_set():
                    try:
                        if DEBUG:
                            print("[Listener] Waiting for speech...")
                        
                        # Listen for user phrase
                        audio = stt_engine.recognizer.listen(source, timeout=5.0, phrase_time_limit=12.0)
                        
                        if self._stop_event.is_set():
                            break

                        if self._on_status_callback:
                            self._on_status_callback("PROCESSING")

                        text = stt_engine.transcribe(audio)
                        if text:
                            if DEBUG:
                                print(f"[Listener Heard]: {text}")
                            if self._on_command_callback:
                                self._on_command_callback(text)
                        
                        if not self._stop_event.is_set() and self._on_status_callback:
                            self._on_status_callback("LISTENING")

                    except sr.WaitTimeoutError:
                        # Normal timeout when no speech detected, continue seamlessly
                        continue
                    except Exception as e:
                        if DEBUG:
                            print(f"[Listener Loop Exception]: {e}")
                        time.sleep(0.5)

        except Exception as e:
            if DEBUG:
                print(f"[Listener Failed to Open Mic]: {e}")
        finally:
            self.is_active = False
            if self._on_status_callback:
                self._on_status_callback("IDLE")


# Singleton instance
voice_listener = VoiceListener()
