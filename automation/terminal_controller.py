"""Terminal and Command Prompt Automation Controller."""
import subprocess
import os
from typing import Tuple
from config.settings import DEBUG


class TerminalController:
    """Controls running commands in Windows CMD, PowerShell, and background processes."""

    @staticmethod
    def run_command_in_cmd(command: str) -> bool:
        """
        Open a visible Windows Command Prompt, run the command, and keep window open.
        """
        try:
            if DEBUG:
                print(f"[TerminalController] Executing in CMD: {command}")
            # 'cmd /k' executes the command and remains open for user review
            subprocess.Popen(
                f'start cmd /k "{command}"',
                shell=True,
                stdin=None,
                stdout=None,
                stderr=None,
                close_fds=True
            )
            return True
        except Exception as e:
            if DEBUG:
                print(f"[TerminalController Error] CMD execution failed: {e}")
            return False

    @staticmethod
    def run_command_in_powershell(command: str) -> bool:
        """
        Open a visible PowerShell window, run command, and keep window open.
        """
        try:
            if DEBUG:
                print(f"[TerminalController] Executing in PowerShell: {command}")
            subprocess.Popen(
                f'start powershell -NoExit -Command "{command}"',
                shell=True,
                stdin=None,
                stdout=None,
                stderr=None,
                close_fds=True
            )
            return True
        except Exception as e:
            if DEBUG:
                print(f"[TerminalController Error] PowerShell execution failed: {e}")
            return False

    @staticmethod
    def execute_background(command: str) -> Tuple[bool, str]:
        """Execute command in background and return captured output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout or result.stderr
            return result.returncode == 0, output.strip()
        except Exception as e:
            return False, str(e)


terminal_ctrl = TerminalController()
