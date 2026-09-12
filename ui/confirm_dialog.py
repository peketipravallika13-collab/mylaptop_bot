"""Confirmation Dialog for Sensitive Actions."""
import tkinter as tk
from tkinter import messagebox
import threading
from typing import Optional


class ConfirmationDialog:
    """Displays a modal or alert to ask user approval before executing sensitive tasks."""

    @staticmethod
    def ask_confirmation(message: str) -> bool:
        """
        Ask user confirmation. Returns True if confirmed, False otherwise.
        Thread-safe execution.
        """
        result = [False]
        event = threading.Event()

        def _show():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            res = messagebox.askyesno(
                "Assistant Security Check",
                f"{message}\n\nDo you want to proceed with this action?",
                parent=root
            )
            result[0] = bool(res)
            root.destroy()
            event.set()

        # Run on a new thread if needed
        t = threading.Thread(target=_show, daemon=True)
        t.start()
        event.wait(timeout=30.0)
        return result[0]
