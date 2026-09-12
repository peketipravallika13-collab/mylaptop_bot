"""Task Planner: Decomposes user commands into actionable steps."""
import re
from typing import List, Dict, Any
from ai.router import command_router
from ai.ai_client import ai_client
from config.settings import DEBUG


class TaskPlanner:
    """Plans multi-step execution graphs for desktop automation."""

    @staticmethod
    def plan(user_command: str) -> List[Dict[str, Any]]:
        """
        Produce a list of action step dictionaries for a given user command.
        """
        # 1. Try instant local match
        local_action = command_router.match_local_command(user_command)
        if local_action:
            return [{
                "action": local_action["action"],
                "parameters": {k: v for k, v in local_action.items() if k not in ("action", "description", "category")},
                "description": local_action.get("description", user_command)
            }]

        # 2. Try LLM Task Planner if API key is configured
        llm_plan = ai_client.plan_tasks(user_command)
        if llm_plan and len(llm_plan) > 0:
            return llm_plan

        # 3. Fallback to heuristic NLP rule-based planner for complex multi-step phrases
        return TaskPlanner._heuristic_plan(user_command)

    @staticmethod
    def _heuristic_plan(command: str) -> List[Dict[str, Any]]:
        """Smart fallback parser for multi-intent commands."""
        clean = command.lower().strip()
        steps: List[Dict[str, Any]] = []

        # Complex YouTube query: "open youtube and play X" or "play X on youtube"
        yt_play_match = re.search(r"(?:open\s+youtube\s+and\s+)?play\s+(?:a\s+|the\s+)?(.+?)(?:\s+on\s+youtube|\s+video)?$", clean)
        if yt_play_match:
            video_query = yt_play_match.group(1).strip()
            return [{
                "action": "search_youtube",
                "parameters": {"query": video_query, "auto_play": True},
                "description": f"Search and play YouTube video: {video_query}"
            }]

        # YouTube search: "open youtube and search X"
        yt_search_match = re.search(r"(?:open\s+youtube\s+and\s+)?search\s+(?:for\s+)?(.+?)(?:\s+on\s+youtube)?$", clean)
        if yt_search_match:
            query = yt_search_match.group(1).strip()
            return [{
                "action": "search_youtube",
                "parameters": {"query": query, "auto_play": False},
                "description": f"Search YouTube for: {query}"
            }]

        # Multi-step: "copy that and open notepad and paste it"
        if "copy" in clean and ("paste" in clean or "open" in clean):
            if "copy" in clean:
                steps.append({"action": "copy_that", "parameters": {}, "description": "Copy selection"})
            
            app_sub = re.search(r"open\s+(notepad|vs\s*code|wordpad)", clean)
            if app_sub:
                steps.append({"action": "open_app", "parameters": {"app_name": app_sub.group(1)}, "description": f"Open {app_sub.group(1)}"})
            
            if "paste" in clean:
                steps.append({"action": "paste_that", "parameters": {}, "description": "Paste into application"})
            
            if steps:
                return steps

        # Generic "open X and type Y"
        type_match = re.match(r"^open\s+([a-zA-Z\s]+?)\s+and\s+type\s+(.+)$", clean)
        if type_match:
            app_name = type_match.group(1).strip()
            text_to_type = type_match.group(2).strip()
            return [
                {"action": "open_app", "parameters": {"app_name": app_name}, "description": f"Open {app_name}"},
                {"action": "type_text", "parameters": {"text": text_to_type}, "description": f"Type '{text_to_type}'"}
            ]

        # Default single search if all else fails
        return [{
            "action": "search_google",
            "parameters": {"query": command},
            "description": f"Search Google for: {command}"
        }]


task_planner = TaskPlanner()
