"""WhatsApp Automation Controller: Contact searching, chat opening, and messaging."""
import time
import urllib.parse
import pyautogui
import pyperclip
from typing import Optional
from automation.browser_controller import browser_ctrl
from automation.windows_controller import win_ctrl
from config.settings import DEBUG


class WhatsAppController:
    """Controls WhatsApp Web and Desktop messaging workflows."""

    WHATSAPP_URL = "https://web.whatsapp.com"

    @classmethod
    def open_whatsapp(cls) -> bool:
        """Open or focus WhatsApp (prefers native Windows desktop app, falls back to web)."""
        # 1. Try focusing existing WhatsApp window/tab first
        if win_ctrl.focus_window_by_title("whatsapp"):
            return True
        # 2. Try launching native Windows WhatsApp desktop app
        try:
            import os
            os.system("start whatsapp:")
            time.sleep(1.5)
            if win_ctrl.focus_window_by_title("whatsapp"):
                return True
        except Exception:
            pass
        # 3. Fallback to WhatsApp Web
        return browser_ctrl.open_browser(cls.WHATSAPP_URL)

    @classmethod
    def open_chat_by_phone(cls, phone_number: str, message: Optional[str] = None) -> bool:
        """Open direct chat URL via phone number (e.g. +919876543210)."""
        clean_phone = "".join(c for c in phone_number if c.isdigit() or c == "+")
        url = f"https://web.whatsapp.com/send?phone={clean_phone}"
        if message:
            url += f"&text={urllib.parse.quote_plus(message)}"
        return browser_ctrl.open_browser(url)

    @classmethod
    def search_and_open_contact(cls, contact_name: str) -> bool:
        """
        Search for a contact name in WhatsApp and open their conversation.
        """
        cls.open_whatsapp()
        time.sleep(2.0)

        try:
            # WhatsApp Desktop & Web search shortcut (Ctrl+F, then Ctrl+Alt+/)
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.3)
            pyautogui.hotkey("ctrl", "alt", "/")
            time.sleep(0.3)
            
            # Type contact name
            pyperclip.copy(contact_name)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.0)
            
            # Press Down arrow and Enter to select first contact result
            pyautogui.press("down")
            time.sleep(0.3)
            pyautogui.press("enter")
            time.sleep(0.5)
            return True
        except Exception as e:
            if DEBUG:
                print(f"[WhatsAppController Error] Opening contact {contact_name}: {e}")
            return False

    @classmethod
    def send_message_to_contact(cls, contact_name: str, message_text: str) -> bool:
        """
        Search contact, open chat, type message, and send.
        """
        success = cls.search_and_open_contact(contact_name)
        if not success:
            return False

        time.sleep(0.8)
        try:
            # Type message text into active input field
            pyperclip.copy(message_text)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.3)
            # Send message
            pyautogui.press("enter")
            return True
        except Exception as e:
            if DEBUG:
                print(f"[WhatsAppController Error] Sending message to {contact_name}: {e}")
            return False

    @classmethod
    def type_and_send_current_chat(cls, message_text: str) -> bool:
        """Type and send in the currently open active chat."""
        try:
            pyperclip.copy(message_text)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.2)
            pyautogui.press("enter")
            return True
        except Exception as e:
            if DEBUG:
                print(f"[WhatsAppController Error] Type and send: {e}")
            return False


whatsapp_ctrl = WhatsAppController()
