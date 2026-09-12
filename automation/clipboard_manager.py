"""Clipboard operations for 'copy that' and 'paste that' commands."""
import time
import pyautogui
import pyperclip
from typing import Optional
from memory.database import memory_db


class ClipboardManager:
    """Manages clipboard actions and contextual text buffer."""

    @staticmethod
    def copy_selection() -> Optional[str]:
        """Perform 'Copy That': simulate Ctrl+C and return copied text."""
        # Backup old clipboard if needed
        old_val = pyperclip.paste()
        
        # Trigger Ctrl+C
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        
        new_val = pyperclip.paste()
        if new_val and new_val != old_val:
            memory_db.set_context("last_copied_text", new_val)
            return new_val
        return new_val

    @staticmethod
    def copy_screen_text() -> Optional[str]:
        """Select all text (Ctrl+A) and Copy (Ctrl+C)."""
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.15)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        val = pyperclip.paste()
        if val:
            memory_db.set_context("last_copied_text", val)
        return val

    @staticmethod
    def paste_selection(text: Optional[str] = None) -> bool:
        """Perform 'Paste That': paste given text or current clipboard."""
        if text:
            pyperclip.copy(text)
            time.sleep(0.1)
        
        pyautogui.hotkey("ctrl", "v")
        return True

    @staticmethod
    def get_text() -> str:
        """Get current clipboard string."""
        return pyperclip.paste()

    @staticmethod
    def set_text(text: str):
        """Set text to clipboard."""
        pyperclip.copy(text)
        memory_db.set_context("last_copied_text", text)


clipboard_mgr = ClipboardManager()
