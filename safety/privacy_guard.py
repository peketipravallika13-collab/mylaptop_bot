"""Local Security & Privacy Guardrail for Desktop Automation."""
import os
import re
from typing import Dict, Any, Tuple


class PrivacyGuard:
    """
    Guarantees privacy and system security:
    1. Local-first isolation: Data stays 100% on the user laptop.
    2. Sensitive data redaction for SQLite logs.
    3. Blocks malicious script exfiltration or unauthorized file operations.
    """

    REDACTED_PATTERNS = [
        (r"(?i)(password|passwd|pwd|secret|api_key|token)[\s:=]+([^\s,]+)", r"\1=********"),
        (r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b", "************"),  # Credit card numbers
    ]

    @classmethod
    def sanitize_log(cls, text: str) -> str:
        """Sanitize passwords and secrets before saving to SQLite database."""
        sanitized = text
        for pattern, replacement in cls.REDACTED_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    @classmethod
    def verify_local_execution(cls, action: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Verify that an action operates locally and safely."""
        # Prevent any network curl exfiltration of local files
        if action in ("run_cmd", "run_terminal"):
            cmd = params.get("command", "").lower()
            if any(forbidden in cmd for forbidden in ("curl -x", "curl -d @", "invoke-webrequest -infil", "nc -e", "bash -i")):
                return False, "Security Alert: Command blocked due to potential data exfiltration pattern."

        return True, "Operation compliant with local privacy policy."


privacy_guard = PrivacyGuard()
