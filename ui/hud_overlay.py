"""HUD Overlay: Floating sleek status widget for the desktop."""
import tkinter as tk
import threading
import time
from typing import Optional


class HUDOverlay:
    """Floating borderless status pill shown on screen."""

    def __init__(self):
        self._root: Optional[tk.Tk] = None
        self._label: Optional[tk.Label] = None
        self._icon_label: Optional[tk.Label] = None
        self._thread: Optional[threading.Thread] = None
        self._ready_event = threading.Event()
        self._hide_timer: Optional[threading.Timer] = None
        self._start_gui_thread()

    def _start_gui_thread(self):
        self._thread = threading.Thread(target=self._run_gui, daemon=True)
        self._thread.start()
        self._ready_event.wait(timeout=3.0)

    def _run_gui(self):
        self._root = tk.Tk()
        self._root.title("Nova HUD")
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", 0.92)
        self._root.config(bg="#1E1E2E")

        # Frame container
        frame = tk.Frame(self._root, bg="#1E1E2E", bd=1, relief="solid", highlightthickness=1, highlightbackground="#313244")
        frame.pack(padx=2, pady=2)

        # Status Icon & Text
        self._icon_label = tk.Label(frame, text="🟢", font=("Segoe UI Emoji", 14), bg="#1E1E2E", fg="#A6E3A1")
        self._icon_label.pack(side="left", padx=(12, 6), pady=8)

        self._label = tk.Label(
            frame,
            text="Personal AI Assistant",
            font=("Segoe UI", 11, "bold"),
            bg="#1E1E2E",
            fg="#CDD6F4"
        )
        self._label.pack(side="left", padx=(0, 16), pady=8)

        # Position at top-center of screen
        screen_w = self._root.winfo_screenwidth()
        w = 340
        h = 44
        x = (screen_w - w) // 2
        y = 24
        self._root.geometry(f"{w}x{h}+{x}+{y}")
        self._root.withdraw()

        self._ready_event.set()
        self._root.mainloop()

    def show_status(self, icon: str, message: str, color: str = "#CDD6F4", auto_hide_seconds: Optional[float] = None):
        """Update and display the HUD overlay."""
        if not self._root:
            return

        def _update():
            if self._label and self._icon_label and self._root:
                self._icon_label.config(text=icon)
                self._label.config(text=message, fg=color)
                self._root.deiconify()
                self._root.lift()

        self._root.after(0, _update)

        # Cancel any previous auto-hide timer
        if self._hide_timer:
            self._hide_timer.cancel()

        if auto_hide_seconds:
            self._hide_timer = threading.Timer(auto_hide_seconds, self.hide)
            self._hide_timer.start()

    def hide(self):
        """Hide the HUD widget."""
        if self._root:
            self._root.after(0, self._root.withdraw)


# Singleton instance
hud = HUDOverlay()
