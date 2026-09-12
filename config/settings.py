"""Configuration settings for Personal AI Desktop Assistant."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# App General
APP_NAME = "Personal AI Assistant"
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Nova")
VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Database
DB_PATH = BASE_DIR / "assistant_memory.db"

# Hotkeys
DEFAULT_HOTKEY = os.getenv("HOTKEY", "ctrl+alt+a")
HOTKEY_PUSH_TO_TALK = "ctrl+alt+v"

# Voice Settings
VOICE_RATE = int(os.getenv("VOICE_RATE", 180))
VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", 1.0))
VOICE_GENDER = os.getenv("VOICE_GENDER", "female")  # 'female' or 'male'
SPEECH_ENERGY_THRESHOLD = 300
SPEECH_PAUSE_THRESHOLD = 0.8

# AI API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gemini-1.5-flash")

# Default Browser (Optional override, None = system default)
PREFERRED_BROWSER = os.getenv("PREFERRED_BROWSER", "chrome")

# Common App Paths / Commands on Windows
KNOWN_APPS = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "browser": "chrome",
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "terminal": "wt",
    "windows terminal": "wt",
    "cmd": "start cmd",
    "command prompt": "start cmd",
    "commandprompt": "start cmd",
    "powershell": "start powershell",
    "file explorer": "explorer",
    "explorer": "explorer",
    "task manager": "taskmgr",
    "taskmgr": "taskmgr",
    "settings": "start ms-settings:",
    "control panel": "control",
    "whatsapp": "start whatsapp:",
    "whatsapp app": "start whatsapp:",
    "spotify": "spotify",
    "paint": "mspaint",
    "wordpad": "write",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "snipping tool": "snippingtool",
}

# Direct Website & Streaming Services Map (opens direct portal, never redirects to Google)
KNOWN_WEBSITES = {
    "youtube": "https://www.youtube.com",
    "hotstar": "https://www.hotstar.com",
    "disney hotstar": "https://www.hotstar.com",
    "disney+ hotstar": "https://www.hotstar.com",
    "jiocinema": "https://www.jiocinema.com",
    "jio cinema": "https://www.jiocinema.com",
    "netflix": "https://www.netflix.com",
    "prime video": "https://www.primevideo.com",
    "amazon prime": "https://www.primevideo.com",
    "spotify": "https://open.spotify.com",
    "chatgpt": "https://chatgpt.com",
    "gmail": "https://mail.google.com",
    "github": "https://www.github.com",
    "whatsapp web": "https://web.whatsapp.com",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
}

KNOWN_FOLDERS = {
    "downloads": str(Path.home() / "Downloads"),
    "documents": str(Path.home() / "Documents"),
    "desktop": str(Path.home() / "Desktop"),
    "pictures": str(Path.home() / "Pictures"),
    "music": str(Path.home() / "Music"),
    "videos": str(Path.home() / "Videos"),
    "projects": "d:\\myprojects",
}
