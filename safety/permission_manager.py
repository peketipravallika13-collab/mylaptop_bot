"""Safety & Permission Manager for Desktop Automation."""
import re
from enum import Enum
from typing import Tuple, Optional


class SafetyLevel(Enum):
    SAFE = "SAFE"                 # Execute automatically without confirmation
    SENSITIVE = "SENSITIVE"       # Prompt user confirmation
    DANGEROUS = "DANGEROUS"       # High risk: explicit dialog or blocked


class SafetyManager:
    """Classifies user tasks and protects the user system."""

    # Keywords that trigger DANGEROUS level
    DANGEROUS_PATTERNS = [
        r"\b(delete|remove|erase|format|wipe)\s+(file|files|folder|directory|disk|drive|c:|d:)\b",
        r"\b(rmdir|del|erase|shred|mkfs)\b",
        r"\b(registry|regedit|format-volume|diskpart)\b",
        r"\b(shutdown|reboot|restart\s+computer)\b",
        r"\b(drop\s+table|drop\s+database)\b",
        r"\b(kill\s+all|taskkill\s+/f)\b",
    ]

    # Keywords that trigger SENSITIVE level
    SENSITIVE_PATTERNS = [
        r"\bclose\s+all\s+(tabs|windows|browsers|apps)\b",
        r"\bclose\s+everything\b",
        r"\b(send\s+email|send\s+message)\b",
        r"\b(download\s+file|install\s+program|pip\s+install)\b",
        r"\b(modify|change)\s+system\b",
        r"\b(empty\s+recycle\s+bin|clear\s+trash)\b",
    ]

    @classmethod
    def evaluate(cls, command_text: str, action_type: Optional[str] = None) -> Tuple[SafetyLevel, str]:
        """
        Evaluate command text and action type to determine safety level.
        Returns (SafetyLevel, reason_string).
        """
        text = command_text.lower().strip()

        # Check dangerous rules
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text):
                return SafetyLevel.DANGEROUS, f"Dangerous command detected matching pattern '{pattern}'"

        # Check sensitive rules
        for pattern in cls.SENSITIVE_PATTERNS:
            if re.search(pattern, text):
                return SafetyLevel.SENSITIVE, f"Sensitive action requested matching pattern '{pattern}'"

        # Check action type explicitly
        if action_type in ("delete_file", "delete_folder", "system_shutdown", "format_drive"):
            return SafetyLevel.DANGEROUS, f"Action type '{action_type}' is classified as dangerous"
        
        if action_type in ("close_all_tabs", "send_email", "kill_process"):
            return SafetyLevel.SENSITIVE, f"Action type '{action_type}' requires confirmation"

        return SafetyLevel.SAFE, "Action is safe to execute"
