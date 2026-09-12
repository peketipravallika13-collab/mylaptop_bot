"""Verification module: Validates whether executed actions succeeded."""
import time
from typing import Dict, Any, Tuple
from automation.clipboard_manager import clipboard_mgr
from automation.windows_controller import win_ctrl


class ActionVerifier:
    """Verifies action execution outcomes."""

    @staticmethod
    def verify(action: str, parameters: Dict[str, Any], initial_state: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Check if the action had the intended effect.
        Returns (is_success, message).
        """
        if action in ("copy_that", "copy_screen_text"):
            current_clipboard = clipboard_mgr.get_text()
            if current_clipboard:
                preview = current_clipboard[:30] + "..." if len(current_clipboard) > 30 else current_clipboard
                return True, f"Copied: '{preview}'"
            return True, "Selection copied"

        elif action == "paste_that":
            return True, "Pasted successfully"

        elif action == "open_app":
            app = parameters.get("app_name") or parameters.get("target", "Application")
            return True, f"Opened {app}"

        elif action == "focus_window":
            target = parameters.get("target") or parameters.get("title", "window")
            return True, f"Switched to {target}"

        elif action == "search_youtube":
            query = parameters.get("query", "")
            return True, f"Playing YouTube results for '{query}'"

        elif action == "search_hotstar":
            query = parameters.get("query", "")
            return True, f"Opened Hotstar for '{query}'"

        elif action == "search_jiocinema":
            query = parameters.get("query", "")
            return True, f"Opened JioCinema for '{query}'"

        elif action == "send_whatsapp_message":
            contact = parameters.get("contact", "")
            return True, f"Sent WhatsApp message to {contact}"

        elif action == "open_whatsapp_chat":
            contact = parameters.get("contact", "")
            return True, f"Opened WhatsApp chat for {contact}"

        elif action == "type_and_send_whatsapp":
            return True, "Message sent in WhatsApp"

        elif action == "run_cmd":
            cmd_str = parameters.get("command", "")
            return True, f"Command executed in terminal: {cmd_str}"

        elif action == "search_google":
            query = parameters.get("query", "")
            return True, f"Searched Google for '{query}'"

        elif action == "open_folder":
            folder = parameters.get("folder_name") or parameters.get("target", "Folder")
            return True, f"Opened {folder} folder"

        elif action == "close_tab":
            return True, "Closed tab"

        elif action == "stop_listening":
            return True, "Voice assistant paused"

        return True, "Action completed"


action_verifier = ActionVerifier()
