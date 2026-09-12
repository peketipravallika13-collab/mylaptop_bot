"""LLM Client for AI Task Planning and Understanding."""
import json
import requests
from typing import Optional, Dict, Any, List
from config.settings import GEMINI_API_KEY, AI_MODEL_NAME, DEBUG


class AIClient:
    """Interacts with Google Gemini or provides offline heuristic fallback."""

    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key

    def plan_tasks(self, user_command: str) -> Optional[List[Dict[str, Any]]]:
        """
        Send user natural language prompt to Gemini and receive a structured JSON task plan.
        """
        if not self.api_key:
            return None

        prompt = f"""
You are the AI Task Planner for a Windows Desktop Voice Assistant.
Convert the user command into a strictly formatted JSON array of executable steps.

Available Action Types:
- "open_app": parameters {{"app_name": "string"}}
- "open_browser": parameters {{"url": "string"}}
- "search_youtube": parameters {{"query": "string", "auto_play": true}}
- "search_google": parameters {{"query": "string"}}
- "open_folder": parameters {{"folder_name": "string"}}
- "copy_that": parameters {{}}
- "paste_that": parameters {{}}
- "click_current": parameters {{}}
- "type_text": parameters {{"text": "string"}}
- "press_key": parameters {{"key": "string"}}
- "close_tab": parameters {{}}
- "close_window": parameters {{}}
- "media_play_pause": parameters {{}}

Return ONLY valid JSON array of objects with keys: "action", "parameters", "description". No markdown wrapping or conversational text.

User Command: "{user_command}"
"""

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL_NAME}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                data = response.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Strip json markdown tags if returned
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                
                parsed = json.loads(raw_text.strip())
                if isinstance(parsed, list):
                    return parsed
            elif DEBUG:
                print(f"[AIClient HTTP Error]: {response.status_code} - {response.text}")
        except Exception as e:
            if DEBUG:
                print(f"[AIClient Exception]: {e}")

        return None


ai_client = AIClient()
