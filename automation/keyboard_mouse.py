"""Keyboard and Mouse Automation controller using PyAutoGUI."""
import time
import pyautogui
from config.settings import DEBUG

# Configure PyAutoGUI settings
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


class KeyboardMouseController:
    """Controls mouse movement, clicks, scrolling, and keyboard actions."""

    @staticmethod
    def click_current():
        """Click at current mouse cursor position."""
        pyautogui.click()

    @staticmethod
    def click_at(x: int, y: int):
        """Click at specific screen coordinates."""
        pyautogui.click(x=x, y=y)

    @staticmethod
    def double_click():
        """Double click at current position."""
        pyautogui.doubleClick()

    @staticmethod
    def right_click():
        """Right click at current position."""
        pyautogui.rightClick()

    @staticmethod
    def scroll(direction: str = "down", clicks: int = 5):
        """Scroll page up or down."""
        scroll_amount = -abs(clicks) * 120 if direction.lower() == "down" else abs(clicks) * 120
        pyautogui.scroll(scroll_amount)

    @staticmethod
    def type_text(text: str, interval: float = 0.02):
        """Type text string."""
        pyautogui.write(text, interval=interval)

    @staticmethod
    def press_key(key: str):
        """Press a single key (enter, space, esc, tab, etc.)."""
        pyautogui.press(key)

    @staticmethod
    def hotkey(*keys):
        """Send combination hotkey (e.g. 'ctrl', 'w')."""
        pyautogui.hotkey(*keys)

    @staticmethod
    def play_pause_media():
        """Toggle media play/pause with Space or Play/Pause key."""
        pyautogui.press("space")

    @staticmethod
    def toggle_fullscreen():
        """Toggle video / browser fullscreen (F or F11)."""
        pyautogui.press("f")


km_ctrl = KeyboardMouseController()
