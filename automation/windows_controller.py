"""Windows Application & Window Manager controller."""
import os
import subprocess
import time
import pyautogui
from typing import Optional, List
from config.settings import KNOWN_APPS, DEBUG
from memory.database import memory_db

try:
    import pygetwindow as gw
except ImportError:
    gw = None


class WindowsController:
    """Manages launching apps and manipulating active windows on Windows OS."""

    @staticmethod
    def launch_app(app_name: str) -> bool:
        """Launch an application by its command or Windows Start Search."""
        name_clean = app_name.lower().strip()
        
        # 1. Check known executable command
        if name_clean in KNOWN_APPS:
            cmd = KNOWN_APPS[name_clean]
            try:
                if DEBUG:
                    print(f"[WindowsController] Launching app via command: {cmd}")
                subprocess.Popen(
                    cmd,
                    shell=True,
                    stdin=None,
                    stdout=None,
                    stderr=None,
                    close_fds=True
                )
                memory_db.set_context("last_opened_app", app_name)
                return True
            except Exception as e:
                if DEBUG:
                    print(f"[WindowsController Error] Launching {app_name}: {e}")

        # 2. Universal Windows Start Search Fallback (only for clean single app names)
        # Avoid typing multi-word sentences with prepositions into Windows search
        words = name_clean.split()
        if len(words) > 2 or any(w in ("in", "that", "and", "or", "chat", "search", "message", "saying") for w in words):
            if DEBUG:
                print(f"[WindowsController] Skipping Windows Start search for complex sentence: {app_name}")
            return False

        try:
            if DEBUG:
                print(f"[WindowsController] Searching and launching via Windows Start: {app_name}")
            pyautogui.press("win")
            time.sleep(0.3)
            pyautogui.write(app_name, interval=0.03)
            time.sleep(0.5)
            pyautogui.press("enter")
            memory_db.set_context("last_opened_app", app_name)
            return True
        except Exception as e:
            if DEBUG:
                print(f"[WindowsController Error] Windows Start search failed: {e}")
            return False

    @staticmethod
    def close_active_window():
        """Close active window using Alt+F4."""
        pyautogui.hotkey("alt", "f4")

    @staticmethod
    def minimize_active_window():
        """Minimize active window using Win+Down."""
        pyautogui.hotkey("win", "down")

    @staticmethod
    def maximize_active_window():
        """Maximize active window using Win+Up."""
        pyautogui.hotkey("win", "up")

    @staticmethod
    def show_desktop():
        """Minimize everything and show desktop using Win+D."""
        pyautogui.hotkey("win", "d")

    @staticmethod
    def switch_window():
        """Switch between active windows using Alt+Tab."""
        pyautogui.hotkey("alt", "tab")

    @staticmethod
    def get_open_windows() -> List[str]:
        """Get titles of all visible windows."""
        if not gw:
            return []
        try:
            titles = [w.title for w in gw.getAllWindows() if w.title and w.visible]
            return titles
        except Exception:
            return []

    @staticmethod
    def focus_window_by_title(partial_title: str) -> bool:
        """Bring a window or tab matching partial title to foreground."""
        if not gw:
            return False
        clean = partial_title.lower().strip()
        try:
            for win in gw.getAllWindows():
                if win.title and clean in win.title.lower():
                    if win.isMinimized:
                        win.restore()
                    win.activate()
                    return True
        except Exception as e:
            if DEBUG:
                print(f"[WindowsController Error] Focusing window: {e}")
        return False


win_ctrl = WindowsController()
