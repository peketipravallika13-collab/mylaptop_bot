"""Windows System Tray Icon and Menu Manager using pystray."""
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu
from typing import Callable, Optional

from voice.listener import voice_listener
from voice.text_to_speech import tts_engine
from execution.task_executor import task_executor
from ui.hud_overlay import hud
from memory.database import memory_db
from config.settings import APP_NAME, VERSION, DEFAULT_HOTKEY


def create_tray_image(is_active: bool = False) -> Image.Image:
    """Generate a clean high-res 64x64 icon for the Windows system tray."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    bg_color = (24, 24, 37, 255)  # Dark slate
    draw.ellipse((4, 4, 60, 60), fill=bg_color, outline=(49, 50, 68), width=2)

    # Microphone / AI icon body
    mic_color = (166, 227, 161) if is_active else (205, 214, 244)  # Mint green vs slate white
    
    # Mic capsule
    draw.rounded_rectangle((24, 14, 40, 36), radius=6, fill=mic_color)
    
    # Mic stand curve
    draw.arc((18, 24, 46, 46), start=0, end=180, fill=mic_color, width=3)
    
    # Mic stand base
    draw.line((32, 46, 32, 52), fill=mic_color, width=3)
    draw.line((24, 52, 40, 52), fill=mic_color, width=3)

    # Glowing indicator dot
    dot_color = (74, 222, 128) if is_active else (148, 163, 184)
    draw.ellipse((46, 10, 56, 20), fill=dot_color)

    return img


class TrayApplication:
    """System Tray Manager for Desktop Assistant."""

    def __init__(self, on_exit_callback: Optional[Callable[[], None]] = None):
        self.on_exit_callback = on_exit_callback
        self.icon: Optional[pystray.Icon] = None
        self._is_listening = False

    def setup(self):
        """Build the tray icon and menu."""
        menu = Menu(
            item("🎤 Start Voice Listener", self.action_start_voice, visible=lambda item: not self._is_listening),
            item("⏹ Stop Voice Listener", self.action_stop_voice, visible=lambda item: self._is_listening),
            Menu.SEPARATOR,
            item("🌐 Browser Controls", Menu(
                item("Open YouTube", lambda: self._run_quick_cmd("open youtube")),
                item("Open Google", lambda: self._run_quick_cmd("open browser")),
                item("Close Active Tab", lambda: self._run_quick_cmd("close tab")),
                item("Close All Tabs", lambda: self._run_quick_cmd("close all tabs")),
            )),
            item("📋 Clipboard", Menu(
                item("Copy That (Ctrl+C)", lambda: self._run_quick_cmd("copy that")),
                item("Paste That (Ctrl+V)", lambda: self._run_quick_cmd("paste that")),
            )),
            item("🖱️ Mouse & Window", Menu(
                item("Click That", lambda: self._run_quick_cmd("click that")),
                item("Scroll Down", lambda: self._run_quick_cmd("scroll down")),
                item("Scroll Up", lambda: self._run_quick_cmd("scroll up")),
                item("Minimize Window", lambda: self._run_quick_cmd("minimize window")),
                item("Show Desktop", lambda: self._run_quick_cmd("show desktop")),
            )),
            Menu.SEPARATOR,
            item("📜 Command History", self.action_show_history),
            item("ℹ️ Help & Hotkeys", self.action_show_help),
            Menu.SEPARATOR,
            item("❌ Exit Assistant", self.action_exit)
        )

        self.icon = pystray.Icon(
            name="PersonalAIAssistant",
            icon=create_tray_image(False),
            title=f"{APP_NAME} (Hotkey: {DEFAULT_HOTKEY.upper()})",
            menu=menu
        )

    def run(self):
        """Run system tray loop."""
        if not self.icon:
            self.setup()
        self.icon.run()

    def update_icon_state(self, is_active: bool):
        """Update tray icon dynamically."""
        self._is_listening = is_active
        if self.icon:
            self.icon.icon = create_tray_image(is_active)
            self.icon.update_menu()

    def action_start_voice(self):
        """Start listening to voice."""
        self.update_icon_state(True)
        hud.show_status("🎤", "Listening for voice...", "#A6E3A1")
        tts_engine.speak("Voice listener activated.")
        
        voice_listener.start_listening(
            on_command=self._on_voice_command,
            on_status=self._on_voice_status
        )

    def action_stop_voice(self):
        """Stop listening to voice."""
        voice_listener.stop_listening()
        self.update_icon_state(False)
        hud.show_status("⏸️", "Voice Listener Paused", "#94E2D5", auto_hide_seconds=2.5)
        tts_engine.speak("Voice listener paused.")

    def toggle_voice(self):
        """Toggle listening on hotkey or tray action."""
        if self._is_listening:
            self.action_stop_voice()
        else:
            self.action_start_voice()

    def _on_voice_command(self, text: str):
        """Handler for speech input."""
        hud.show_status("⚡", f"Thinking: {text}", "#F9E2AF")
        success, response_msg = task_executor.execute_command(text)
        
        icon = "✅" if success else "❌"
        color = "#A6E3A1" if success else "#F38BA8"
        hud.show_status(icon, response_msg, color, auto_hide_seconds=4.0)
        
        tts_engine.speak(response_msg)

    def _on_voice_status(self, status: str):
        """Handle voice listener status updates."""
        if status == "LISTENING":
            hud.show_status("🎤", "Listening...", "#A6E3A1")
        elif status == "CALIBRATING":
            hud.show_status("⚙️", "Calibrating audio...", "#89B4FA")
        elif status == "PROCESSING":
            hud.show_status("⏳", "Processing speech...", "#F9E2AF")
        elif status == "IDLE":
            self.update_icon_state(False)

    def _run_quick_cmd(self, cmd_text: str):
        """Execute a quick command from menu."""
        hud.show_status("⚡", f"Executing: {cmd_text}", "#89B4FA")
        success, response_msg = task_executor.execute_command(cmd_text)
        hud.show_status("✅" if success else "❌", response_msg, "#A6E3A1" if success else "#F38BA8", auto_hide_seconds=3.0)
        tts_engine.speak(response_msg)

    def action_show_history(self):
        """Show history viewer window."""
        def _view():
            root = tk.Tk()
            root.title(f"{APP_NAME} - Command History")
            root.geometry("640x420")
            root.config(bg="#1E1E2E")
            root.attributes("-topmost", True)

            title_label = tk.Label(root, text="Command History", font=("Segoe UI", 13, "bold"), bg="#1E1E2E", fg="#CDD6F4")
            title_label.pack(anchor="w", padx=16, pady=(14, 8))

            cols = ("Timestamp", "Command", "Status", "Result")
            tree = ttk.Treeview(root, columns=cols, show="headings", height=14)
            for c in cols:
                tree.heading(c, text=c)
            tree.column("Timestamp", width=140)
            tree.column("Command", width=180)
            tree.column("Status", width=80)
            tree.column("Result", width=200)

            history = memory_db.get_recent_history(30)
            for h in history:
                tree.insert("", "end", values=(h["timestamp"][:19], h["raw_command"], h["status"], h["result_message"]))

            tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
            root.mainloop()

        t = threading.Thread(target=_view, daemon=True)
        t.start()

    def action_show_help(self):
        """Show help dialog."""
        def _show():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showinfo(
                "Personal AI Assistant Help",
                f"Assistant Name: {APP_NAME} v{VERSION}\n"
                f"Global Hotkey: {DEFAULT_HOTKEY.upper()}\n\n"
                "Example Commands:\n"
                "• 'Open YouTube and play Python FastAPI tutorial'\n"
                "• 'Open browser / Open Chrome'\n"
                "• 'Copy that' / 'Paste that'\n"
                "• 'Click that' / 'Double click'\n"
                "• 'Scroll down' / 'Scroll up'\n"
                "• 'Open Notepad / VS Code / Calculator'\n"
                "• 'Open Downloads / Documents'\n"
                "• 'Close this tab' / 'Close window'\n"
                "• 'Stop listening'",
                parent=root
            )
            root.destroy()
        
        t = threading.Thread(target=_show, daemon=True)
        t.start()

    def action_exit(self):
        """Stop voice, hide overlays, and exit."""
        voice_listener.stop_listening()
        tts_engine.stop()
        hud.hide()
        if self.icon:
            self.icon.stop()
        if self.on_exit_callback:
            self.on_exit_callback()


tray_app = TrayApplication()
