"""Task Executor: Coordinates task execution, safety, and verifications."""
import time
from typing import Dict, Any, Tuple, Optional, Callable
from safety.permission_manager import SafetyManager, SafetyLevel
from ai.task_planner import task_planner
from automation.browser_controller import browser_ctrl
from automation.windows_controller import win_ctrl
from automation.keyboard_mouse import km_ctrl
from automation.clipboard_manager import clipboard_mgr
from automation.file_controller import file_ctrl
from execution.verifier import action_verifier
from memory.database import memory_db
from config.settings import DEBUG


class TaskExecutor:
    """Executes planned steps across automation subsystems safely."""

    def __init__(self, confirm_callback: Optional[Callable[[str], bool]] = None):
        self.confirm_callback = confirm_callback

    def execute_command(self, raw_command: str) -> Tuple[bool, str]:
        """
        Main pipeline entry point for a voice command.
        Returns (success: bool, user_response_message: str).
        """
        start_time = time.time()
        
        # 1. Safety Pre-check
        safety_level, reason = SafetyManager.evaluate(raw_command)
        if safety_level == SafetyLevel.DANGEROUS:
            if self.confirm_callback:
                approved = self.confirm_callback(f"Dangerous Action Warning: {reason}\nProceed?")
                if not approved:
                    msg = "Dangerous operation cancelled for your safety."
                    memory_db.log_command(raw_command, "SAFETY", "CANCELLED", "CANCELLED", msg)
                    return False, msg
            else:
                msg = f"Action blocked: {reason}"
                memory_db.log_command(raw_command, "SAFETY", "BLOCKED", "CANCELLED", msg)
                return False, msg

        elif safety_level == SafetyLevel.SENSITIVE:
            if self.confirm_callback:
                approved = self.confirm_callback(f"Confirmation Required: {raw_command}\nContinue?")
                if not approved:
                    msg = "Action cancelled by user."
                    memory_db.log_command(raw_command, "CONFIRMATION", "CANCELLED", "CANCELLED", msg)
                    return False, msg

        # 2. Plan the tasks
        steps = task_planner.plan(raw_command)
        if not steps:
            msg = f"I didn't understand the command '{raw_command}'"
            return False, msg

        # 3. Execute each step
        last_msg = "Done."
        for idx, step in enumerate(steps):
            action = step.get("action", "")
            params = step.get("parameters", {})
            
            if DEBUG:
                print(f"[Executor Step {idx+1}/{len(steps)}] Action: {action}, Params: {params}")

            success, msg = self._dispatch_action(action, params)
            if not success:
                elapsed_ms = int((time.time() - start_time) * 1000)
                memory_db.log_command(raw_command, "AUTOMATION", str(steps), "FAILED", msg, elapsed_ms)
                return False, f"Failed at step {idx+1}: {msg}"
            
            # Verify outcome
            _, last_msg = action_verifier.verify(action, params)

        elapsed_ms = int((time.time() - start_time) * 1000)
        memory_db.log_command(raw_command, "AUTOMATION", str(steps), "SUCCESS", last_msg, elapsed_ms)
        return True, last_msg

    def _dispatch_action(self, action: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Dispatch a single atomic action to its controller."""
        try:
            # Clipboard
            if action == "copy_that":
                clipboard_mgr.copy_selection()
                return True, "Copied selection"

            elif action == "copy_screen_text":
                clipboard_mgr.copy_screen_text()
                return True, "Copied screen text"

            elif action == "paste_that":
                clipboard_mgr.paste_selection()
                return True, "Pasted"

            # Mouse
            elif action == "click_current":
                km_ctrl.click_current()
                return True, "Clicked"

            elif action == "double_click":
                km_ctrl.double_click()
                return True, "Double clicked"

            elif action == "right_click":
                km_ctrl.right_click()
                return True, "Right clicked"

            elif action == "scroll_down":
                km_ctrl.scroll("down", clicks=params.get("clicks", 5))
                return True, "Scrolled down"

            elif action == "scroll_up":
                km_ctrl.scroll("up", clicks=params.get("clicks", 5))
                return True, "Scrolled up"

            elif action == "type_text":
                km_ctrl.type_text(params.get("text", ""))
                return True, "Typed text"

            elif action == "press_key":
                km_ctrl.press_key(params.get("key", "enter"))
                return True, f"Pressed {params.get('key')}"

            # Media
            elif action == "media_play_pause":
                km_ctrl.play_pause_media()
                return True, "Toggled media"

            elif action == "fullscreen":
                km_ctrl.toggle_fullscreen()
                return True, "Fullscreen toggled"

            # Browser & Streaming
            elif action == "open_browser":
                browser_ctrl.open_browser(params.get("url"))
                return True, "Browser opened"

            elif action == "open_youtube":
                browser_ctrl.open_youtube()
                return True, "YouTube opened"

            elif action == "search_youtube":
                browser_ctrl.search_youtube(
                    query=params.get("query", ""),
                    auto_play=params.get("auto_play", True)
                )
                return True, "YouTube searched"

            elif action == "search_hotstar":
                browser_ctrl.search_hotstar(params.get("query", ""))
                return True, "Hotstar searched"

            elif action == "search_jiocinema":
                browser_ctrl.search_jiocinema(params.get("query", ""))
                return True, "JioCinema searched"

            elif action == "search_google":
                browser_ctrl.search_google(params.get("query", ""))
                return True, "Google searched"

            elif action == "close_tab":
                browser_ctrl.close_current_tab()
                return True, "Tab closed"

            elif action == "new_tab":
                browser_ctrl.new_tab()
                return True, "New tab opened"

            elif action == "reopen_tab":
                browser_ctrl.reopen_tab()
                return True, "Tab restored"

            elif action == "close_all_tabs":
                browser_ctrl.close_all_tabs()
                return True, "Browser closed"

            # WhatsApp Automation
            elif action == "send_whatsapp_message":
                from automation.whatsapp_controller import whatsapp_ctrl
                contact = params.get("contact", "")
                message = params.get("message", "")
                success = whatsapp_ctrl.send_message_to_contact(contact, message)
                return success, f"Sent WhatsApp message to {contact}"

            elif action == "open_whatsapp_chat":
                from automation.whatsapp_controller import whatsapp_ctrl
                contact = params.get("contact", "")
                success = whatsapp_ctrl.search_and_open_contact(contact)
                return success, f"Opened WhatsApp chat for {contact}"

            elif action == "type_and_send_whatsapp":
                from automation.whatsapp_controller import whatsapp_ctrl
                message = params.get("message", "")
                success = whatsapp_ctrl.type_and_send_current_chat(message)
                return success, f"Typed and sent: '{message}'"

            # Terminal Execution
            elif action == "run_cmd":
                from automation.terminal_controller import terminal_ctrl
                cmd_str = params.get("command", "")
                success = terminal_ctrl.run_command_in_cmd(cmd_str)
                return success, f"Executed in Command Prompt: {cmd_str}"

            elif action == "run_powershell":
                from automation.terminal_controller import terminal_ctrl
                cmd_str = params.get("command", "")
                success = terminal_ctrl.run_command_in_powershell(cmd_str)
                return success, f"Executed in PowerShell: {cmd_str}"

            # Windows Management
            elif action == "focus_window":
                target = params.get("target") or params.get("title", "")
                found = win_ctrl.focus_window_by_title(target)
                if not found:
                    # Check if target is a known website (e.g. YouTube) and open it if not already open
                    from config.settings import KNOWN_WEBSITES
                    if target.lower() in KNOWN_WEBSITES:
                        browser_ctrl.open_browser(KNOWN_WEBSITES[target.lower()])
                        return True, f"Opened {target.title()} tab"
                    return False, f"Could not find open window or tab matching '{target}'"
                return True, f"Switched to {target}"

            elif action == "open_app":
                app_name = params.get("app_name") or params.get("target", "")
                win_ctrl.launch_app(app_name)
                return True, f"Launched {app_name}"

            elif action == "close_window":
                win_ctrl.close_active_window()
                return True, "Window closed"

            elif action == "minimize_window":
                win_ctrl.minimize_active_window()
                return True, "Window minimized"

            elif action == "maximize_window":
                win_ctrl.maximize_active_window()
                return True, "Window maximized"

            elif action == "show_desktop":
                win_ctrl.show_desktop()
                return True, "Desktop shown"

            elif action == "switch_window":
                win_ctrl.switch_window()
                return True, "Switched window"

            # Files
            elif action == "open_folder":
                folder_name = params.get("folder_name") or params.get("target", "")
                file_ctrl.open_folder(folder_name)
                return True, f"Opened {folder_name}"

            elif action == "stop_listening":
                # Will be handled in main controller
                return True, "Paused"

            else:
                return False, f"Unknown action '{action}'"

        except Exception as e:
            if DEBUG:
                print(f"[Dispatch Error] {action}: {e}")
            return False, str(e)


task_executor = TaskExecutor()
