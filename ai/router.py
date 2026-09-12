"""Hybrid Command Router: Fast Local Rule Engine vs AI Engine with Phonetic & Typo Normalizer."""
import re
from typing import Optional, Dict, Any
from config.settings import KNOWN_WEBSITES, KNOWN_APPS


class CommandRouter:
    """
    Evaluates incoming voice commands, cleans STT errors & phonetic slang,
    and matches instant desktop actions.
    """

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Correct common speech-to-text slips, phonetic typos, and redundant filler words."""
        clean = text.lower().strip()

        # 1. Strip conversational prefixes
        clean = re.sub(r"^(?:hlo|helo|hello|hey|hi|yo|ok|okay|please|assistant|can\s+you|could\s+you)\s+", "", clean).strip()

        # 2. Phonetic & Typo Replacements
        replacements = [
            (r"\b(onpin|onpn|opined|opin\w*|opne\w*|opn\w*|ope)\b", "open"),
            (r"\b(whats\s*app|what's\s*app)\b", "whatsapp"),
            (r"\b(coppy|copey|copi|copyy)\b", "copy"),
            (r"\b(past|paaste|peyst)\b", "paste"),
            (r"\b(crome|chome|chrom)\b", "chrome"),
            (r"\b(hostar|hotstarr|hostarr|jio\s*hostar|jio\s*hotstar)\b", "hotstar"),
            (r"\b(jiocinema|jio\s*cinema)\b", "jiocinema"),
            (r"\b(loptop|leptop|labtop)\b", "laptop"),
            (r"\b(tha|da|de)\b", "the"),
            (r"\b(clik|clck|cleck)\b", "click"),
            (r"\b(serch|surch|serach)\b", "search"),
        ]
        for pattern, replacement in replacements:
            clean = re.sub(pattern, replacement, clean)

        return clean

    @classmethod
    def match_local_command(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        Check if text matches known instant desktop actions with smart parsing.
        """
        clean = cls.normalize_text(text)

        # 1. Clipboard actions ("copy that", "copy this content", "copy my current text screen content")
        if re.search(r"\bcopy\s+(?:my\s+)?(?:current\s+)?(?:text\s+)?(?:screen\s+content|all\s+text|everything)\b", clean):
            return {"action": "copy_screen_text", "category": "CLIPBOARD", "description": "Copy screen text content"}

        if clean in ("copy that", "copy", "copy text", "copy this", "copy this content", "copy content"):
            return {"action": "copy_that", "category": "CLIPBOARD", "description": "Copy current selection"}
        
        if clean in ("paste that", "paste", "paste here", "paste this", "paste it", "paste content"):
            return {"action": "paste_that", "category": "CLIPBOARD", "description": "Paste from clipboard"}

        # 2. Mouse actions ("click that", "click here", "click send button", "click send", "click something message")
        if clean in ("click send", "click send button", "send message", "send", "click on send", "send button"):
            return {"action": "press_key", "key": "enter", "category": "KEYBOARD", "description": "Send message"}

        if clean in ("click that", "click here", "click", "left click", "click something", "click message", "click something message"):
            return {"action": "click_current", "category": "MOUSE", "description": "Click current position"}
        
        if clean in ("double click", "double click that"):
            return {"action": "double_click", "category": "MOUSE", "description": "Double click current position"}

        if clean in ("right click", "right click that"):
            return {"action": "right_click", "category": "MOUSE", "description": "Right click current position"}

        # 3. Typing in active app / message box ("type hello world", "type message how are you")
        type_match = re.match(r"^(?:type\s+(?:message\s+|this\s+)?|write\s+)(.+)$", clean)
        if type_match and not clean.startswith("type this and send"):
            text_to_type = type_match.group(1).strip()
            return {"action": "type_text", "text": text_to_type, "category": "KEYBOARD", "description": f"Type: '{text_to_type}'"}

        # 4. WhatsApp In-Depth Automation
        # Case A: Full message -> "send whatsapp message to John saying Hello" or "open whatsapp and message Mom Hello"
        wa_msg_match = re.search(r"(?:send\s+)?(?:whatsapp\s+message\s+to|message\s+to|message)\s+([a-zA-Z0-9\s]+?)(?:\s+on\s+whatsapp)?\s+(?:saying|that|with\s+text)\s+(.+)$", clean) or \
                       re.search(r"(?:open\s+whatsapp\s+(?:and\s+|in\s+that\s+)?message\s+)([a-zA-Z0-9\s]+?)\s+(?:saying|that|with\s+text)?\s*(.+)$", clean)
        if wa_msg_match:
            contact = wa_msg_match.group(1).strip()
            msg = wa_msg_match.group(2).strip()
            return {"action": "send_whatsapp_message", "contact": contact, "message": msg, "category": "WHATSAPP", "description": f"Send WhatsApp message to {contact}: '{msg}'"}

        # Case B: Open specific chat -> "open whatsapp and in that Rahul chat", "open whatsapp app and in the whatsapp app search the rachel rachabanda chat"
        wa_chat_match = re.search(r"^open\s+whatsapp(?:\s+app)?\s+(?:and\s+)?in\s+(?:the\s+whatsapp\s+(?:app\s+)?)?(?:that\s+)?(?:search\s+)?(?:the\s+)?([a-zA-Z0-9\s]+?)(?:\s+chat|\s+conversation)?$", clean) or \
                        re.search(r"^open\s+whatsapp(?:\s+app)?\s+(?:(?:and\s+)?in\s+that\s+|(?:and\s+)?(?:search|find|chat\s+with)\s+|chat\s+of\s+)?([a-zA-Z0-9\s]+?)(?:\s+chat|\s+conversation)?(?:\s+on\s+whatsapp|\s+in\s+whatsapp)?$", clean) or \
                        re.search(r"^in\s+whatsapp\s+(?:app\s+)?(?:search\s+|open\s+)(?:the\s+)?([a-zA-Z0-9\s]+?)(?:\s+chat|\s+conversation)?$", clean) or \
                        re.search(r"^open\s+(?:chat\s+of\s+|conversation\s+with\s+)([a-zA-Z0-9\s]+?)\s+on\s+whatsapp$", clean)
        if wa_chat_match:
            contact = wa_chat_match.group(1).strip()
            # If the user just said "open whatsapp" or "open whatsapp app"
            if contact in ("", "whatsapp", "app", "whatsapp app", "the whatsapp"):
                return {"action": "open_browser", "url": "https://web.whatsapp.com", "category": "BROWSER", "description": "Open WhatsApp"}
            return {"action": "open_whatsapp_chat", "contact": contact, "category": "WHATSAPP", "description": f"Open WhatsApp chat for {contact}"}

        wa_type_send = re.search(r"^(?:type\s+this\s+|type\s+)(.+?)(?:\s+and\s+send|\s+in\s+whatsapp\s+and\s+send)$", clean)
        if wa_type_send:
            msg = wa_type_send.group(1).strip()
            return {"action": "type_and_send_whatsapp", "message": msg, "category": "WHATSAPP", "description": f"Type and send: '{msg}'"}

        # 5. YouTube In-Depth Automation
        # "open youtube and in that python tutorial", "in youtube open python fastapi tutorial", "open youtube search X"
        yt_search_match = re.search(r"^open\s+youtube\s+(?:(?:and\s+)?in\s+that\s+|(?:and\s+)?search\s+(?:for\s+)?|search\s+on\s+youtube\s+(?:for\s+)?)(.+)$", clean) or \
                          re.search(r"^in\s+youtube\s+(?:search|open|play)\s+(.+)$", clean) or \
                          re.search(r"^open\s+(?:youtube\s+)?(.+?)\s+tutorial(?:\s+details|\s+on\s+youtube)?$", clean)
        if yt_search_match:
            query = yt_search_match.group(1).strip()
            if query not in ("", "youtube", "app", "the youtube"):
                return {"action": "search_youtube", "query": query, "auto_play": True, "category": "BROWSER", "description": f"Search YouTube for: {query}"}

        # 6. Streaming Search ("open jio hotstar in that bigboss live", "open telugu bigboss in hotstar season 10")
        hotstar_search_match = re.search(r"(?:open\s+)?(?:hotstar\s+in\s+that\s+|in\s+hotstar\s+)(.+)$", clean) or \
                               re.search(r"(?:open\s+)?(.+?)\s+in\s+(?:the\s+)?hotstar(?:\s+(.+))?$", clean)
        if hotstar_search_match:
            q1 = hotstar_search_match.group(1) or ""
            q2 = hotstar_search_match.group(2) if hotstar_search_match.lastindex >= 2 and hotstar_search_match.group(2) else ""
            query = f"{q1} {q2}".strip()
            if query and query != "hotstar":
                return {"action": "search_hotstar", "query": query, "category": "BROWSER", "description": f"Search Hotstar for: {query}"}

        jiocinema_search_match = re.search(r"(?:open\s+)?(?:jiocinema\s+in\s+that\s+|in\s+jiocinema\s+)(.+)$", clean) or \
                                 re.search(r"(?:open\s+)?(.+?)\s+in\s+(?:the\s+)?jiocinema(?:\s+(.+))?$", clean)
        if jiocinema_search_match:
            q1 = jiocinema_search_match.group(1) or ""
            q2 = jiocinema_search_match.group(2) if jiocinema_search_match.lastindex >= 2 and jiocinema_search_match.group(2) else ""
            query = f"{q1} {q2}".strip()
            if query and query != "jiocinema":
                return {"action": "search_jiocinema", "query": query, "category": "BROWSER", "description": f"Search JioCinema for: {query}"}

        # 7. Scrolling & Media
        if clean in ("scroll down", "go down", "page down"):
            return {"action": "scroll_down", "category": "MOUSE", "description": "Scroll down"}
        
        if clean in ("scroll up", "go up", "page up"):
            return {"action": "scroll_up", "category": "MOUSE", "description": "Scroll up"}

        if clean in ("pause", "play", "play video", "pause video", "toggle play"):
            return {"action": "media_play_pause", "category": "MEDIA", "description": "Toggle media playback"}

        if clean in ("fullscreen", "make it full screen", "full screen"):
            return {"action": "fullscreen", "category": "MEDIA", "description": "Toggle fullscreen"}

        # 8. Tab / Window Switcher ("open youtube that i have already keep opened in chrome", "switch to youtube tab")
        already_open_match = re.search(r"(?:open\s+)?([a-zA-Z0-9\s]+?)\s+(?:that\s+i\s+have\s+)?already\s+(?:keep\s+|kept\s+)?(?:opened|open|running)", clean)
        if already_open_match:
            target = already_open_match.group(1).replace("the", "").strip()
            return {"action": "focus_window", "target": target, "category": "WINDOWS", "description": f"Switch to existing {target} window/tab"}

        switch_match = re.match(r"^(?:switch\s+to|give\s+me\s+the|bring\s+up|focus|show)\s+(.+?)(?:\s+tab|\s+window)?$", clean)
        if switch_match:
            target_title = switch_match.group(1).strip()
            if target_title not in ("window", "app", "tab", "active window"):
                return {"action": "focus_window", "target": target_title, "category": "WINDOWS", "description": f"Switch to {target_title}"}

        # 9. Tab & Window Management
        if clean in ("close this tab", "close tab", "close the tab"):
            return {"action": "close_tab", "category": "BROWSER", "description": "Close active browser tab"}

        if clean in ("new tab", "open new tab", "create tab"):
            return {"action": "new_tab", "category": "BROWSER", "description": "Open new browser tab"}

        if clean in ("reopen tab", "restore tab", "undo close tab"):
            return {"action": "reopen_tab", "category": "BROWSER", "description": "Reopen closed browser tab"}

        if clean in ("close all tabs", "close browser"):
            return {"action": "close_all_tabs", "category": "BROWSER", "description": "Close all browser tabs"}

        if clean in ("close window", "close this window", "close app"):
            return {"action": "close_window", "category": "WINDOWS", "description": "Close active window"}

        if clean in ("minimize window", "minimize", "hide window"):
            return {"action": "minimize_window", "category": "WINDOWS", "description": "Minimize active window"}

        if clean in ("maximize window", "maximize"):
            return {"action": "maximize_window", "category": "WINDOWS", "description": "Maximize active window"}

        if clean in ("show desktop", "minimize all"):
            return {"action": "show_desktop", "category": "WINDOWS", "description": "Show Windows desktop"}

        if clean in ("switch window", "next window", "switch app"):
            return {"action": "switch_window", "category": "WINDOWS", "description": "Switch active window"}

        # 10. Direct Website Portals ("open hotstar", "open jiocinema", "open youtube", "open netflix", "open whatsapp")
        for site_key, site_url in KNOWN_WEBSITES.items():
            if clean in (f"open {site_key}", f"open {site_key} app", f"go to {site_key}", f"launch {site_key}", f"open {site_key} tab", f"open the {site_key}"):
                return {"action": "open_browser", "url": site_url, "category": "BROWSER", "description": f"Open {site_key.title()}"}

        # 11. Folder Launching ("open this folder", "open downloads folder", "open projects folder", "open folder <path>")
        folder_match = re.match(r"^open\s+(?:this\s+folder|folder\s+(.+)|(downloads|documents|desktop|pictures|music|videos|projects)(\s+folder)?)$", clean)
        if folder_match:
            folder_name = folder_match.group(1) or folder_match.group(2) or "projects"
            return {"action": "open_folder", "target": folder_name, "category": "FILE", "description": f"Open folder: {folder_name}"}

        # 12. Terminal / Command Prompt Task Execution ("open cmd and run dir", "run command in terminal pip install numpy")
        term_run_match = re.search(r"^(?:open\s+(?:command\s+prompt|cmd|terminal)\s+and\s+run\s+|run\s+(?:command\s+)?(?:in\s+(?:cmd|terminal|command\s+prompt|powershell)\s+)?|execute\s+(?:in\s+(?:cmd|terminal|powershell)\s+)?)(.+)$", clean)
        if term_run_match and not clean.startswith("open"):
            cmd_to_run = term_run_match.group(1).strip()
            return {"action": "run_cmd", "command": cmd_to_run, "category": "TERMINAL", "description": f"Run command: {cmd_to_run}"}

        # 13. Strict Laptop Application Launching ("open command prompt in my laptop not chrome", "open cmd", "open notepad")
        # Must strictly be a known application or short name (not sentences)
        app_clean = re.sub(r"\s+(?:in\s+my\s+laptop\s+not\s+chrome|in\s+my\s+laptop|on\s+my\s+laptop|on\s+laptop|in\s+laptop|on\s+pc|app)$", "", clean)
        app_match = re.match(r"^(?:open|launch|start)\s+([a-zA-Z0-9_\-\s]{1,30})$", app_clean)
        if app_match:
            candidate = app_match.group(1).strip()
            # If candidate is a known application
            if candidate in KNOWN_APPS:
                return {"action": "open_app", "target": candidate, "category": "WINDOWS", "description": f"Open {candidate}"}
            
            # If short single app word and not a sentence with verbs/prepositions
            words = candidate.split()
            if len(words) <= 2 and not any(w in ("in", "that", "and", "or", "search", "google", "youtube", "to", "with") for w in words):
                return {"action": "open_app", "target": candidate, "category": "WINDOWS", "description": f"Open application: {candidate}"}

        # 14. Google Search
        google_match = re.match(r"^(?:search\s+google\s+(?:for\s+)?|search\s+(?:for\s+)?|google\s+)(.+)$", clean)
        if google_match and not clean.startswith("open"):
            query = google_match.group(1).strip()
            return {"action": "search_google", "query": query, "category": "BROWSER", "description": f"Search Google for: {query}"}

        # 15. Listening Control
        if clean in ("stop listening", "stop voice", "go to sleep", "sleep", "pause listening"):
            return {"action": "stop_listening", "category": "SYSTEM", "description": "Stop listening to voice commands"}

        return None


command_router = CommandRouter()
