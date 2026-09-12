"""Browser and YouTube automation controller."""
import webbrowser
import urllib.parse
import time
import pyautogui
from typing import Optional
from config.settings import PREFERRED_BROWSER, DEBUG


pyautogui.FAILSAFE = False


class BrowserController:
    """Controls browser navigation, search, YouTube actions, and tabs."""

    @staticmethod
    def open_browser(url: Optional[str] = None) -> bool:
        """Open browser to homepage or specific URL."""
        target_url = url if url else "https://www.google.com"
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        try:
            if DEBUG:
                print(f"[BrowserController] Opening URL: {target_url}")
            webbrowser.open(target_url, new=2)
            return True
        except Exception as e:
            if DEBUG:
                print(f"[BrowserController Error] Opening browser: {e}")
            return False

    @staticmethod
    def search_google(query: str) -> bool:
        """Search query on Google."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        return BrowserController.open_browser(url)

    @staticmethod
    def search_hotstar(query: str) -> bool:
        """Search directly on Disney+ Hotstar."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.hotstar.com/in/explore?q={encoded}"
        return BrowserController.open_browser(url)

    @staticmethod
    def search_jiocinema(query: str) -> bool:
        """Search directly on JioCinema."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.jiocinema.com/search/{encoded}"
        return BrowserController.open_browser(url)

    @staticmethod
    def open_youtube() -> bool:
        """Open YouTube homepage."""
        return BrowserController.open_browser("https://www.youtube.com")

    @staticmethod
    def search_youtube(query: str, auto_play: bool = True) -> bool:
        """Search YouTube and optionally trigger playback."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        success = BrowserController.open_browser(url)
        
        if success and auto_play:
            try:
                time.sleep(2.0)
                pyautogui.press("tab")
                time.sleep(0.3)
                pyautogui.press("enter")
            except Exception as e:
                if DEBUG:
                    print(f"[YouTube Playback Navigation Notice]: {e}")
            
        return success

    @staticmethod
    def close_current_tab():
        """Close active browser tab using Ctrl+W."""
        pyautogui.hotkey("ctrl", "w")

    @staticmethod
    def new_tab():
        """Open a new browser tab using Ctrl+T."""
        pyautogui.hotkey("ctrl", "t")

    @staticmethod
    def reopen_tab():
        """Reopen last closed tab using Ctrl+Shift+T."""
        pyautogui.hotkey("ctrl", "shift", "t")

    @staticmethod
    def close_all_tabs():
        """Close current browser window using Ctrl+Shift+W or Alt+F4."""
        pyautogui.hotkey("ctrl", "shift", "w")


browser_ctrl = BrowserController()
