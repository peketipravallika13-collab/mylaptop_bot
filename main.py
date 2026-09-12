"""Personal AI Desktop Assistant - Application Entry Point."""
import sys
import os
import signal
import threading
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.settings import APP_NAME, VERSION, DEFAULT_HOTKEY, DEBUG
from execution.task_executor import task_executor
from ui.confirm_dialog import ConfirmationDialog
from ui.tray import tray_app
from ui.hud_overlay import hud

# Hook confirmation callback to safety executor
task_executor.confirm_callback = ConfirmationDialog.ask_confirmation


def setup_global_hotkey():
    """Register global hotkey (e.g. Ctrl+Alt+A) to toggle voice listening."""
    try:
        import keyboard
        keyboard.add_hotkey(DEFAULT_HOTKEY, tray_app.toggle_voice)
        if DEBUG:
            print(f"[Hotkeys] Global hotkey registered: {DEFAULT_HOTKEY}")
    except Exception as e:
        if DEBUG:
            print(f"[Hotkeys Warning] Could not hook keyboard library: {e}. Trying pynput fallback...")
        try:
            from pynput import keyboard as pynput_kb
            # Fallback simple listener if needed
        except Exception as e2:
            if DEBUG:
                print(f"[Hotkeys Error] Hotkey listener disabled: {e2}")


def main():
    """Start Assistant in System Tray."""
    print(f"==================================================")
    print(f"   {APP_NAME} v{VERSION}")
    print(f"   Running in Windows System Tray")
    print(f"   Toggle Voice Hotkey: {DEFAULT_HOTKEY.upper()}")
    print(f"==================================================")

    # Register hotkey
    setup_global_hotkey()

    # Show initial welcome status in HUD
    hud.show_status("🟢", f"{APP_NAME} Ready", "#A6E3A1", auto_hide_seconds=3.0)

    # Run system tray event loop (blocks main thread until Exit)
    try:
        tray_app.run()
    except KeyboardInterrupt:
        tray_app.action_exit()


if __name__ == "__main__":
    main()
