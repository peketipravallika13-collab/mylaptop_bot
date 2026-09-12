"""Unit & Integration Tests for Personal AI Desktop Assistant."""
import unittest
from memory.database import MemoryDatabase
from safety.permission_manager import SafetyManager, SafetyLevel
from ai.router import command_router
from ai.task_planner import task_planner
from execution.verifier import action_verifier
from pathlib import Path
import tempfile


class TestPersonalAIAssistant(unittest.TestCase):

    def setUp(self):
        # Temp database for tests
        self.temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db = MemoryDatabase(Path(self.temp_db_file.name))

    def tearDown(self):
        try:
            self.temp_db_file.close()
            Path(self.temp_db_file.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_database_logging(self):
        """Test SQLite logging and retrieval."""
        row_id = self.db.log_command(
            raw_command="open youtube",
            category="BROWSER",
            action_plan="[{'action': 'open_youtube'}]",
            status="SUCCESS",
            result_message="Opened YouTube",
            execution_time_ms=120
        )
        self.assertGreater(row_id, 0)
        
        history = self.db.get_recent_history(5)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["raw_command"], "open youtube")
        self.assertEqual(history[0]["status"], "SUCCESS")

    def test_safety_manager_classification(self):
        """Test safe, sensitive, and dangerous command evaluation."""
        # Safe
        level, _ = SafetyManager.evaluate("open youtube and play python tutorial")
        self.assertEqual(level, SafetyLevel.SAFE)

        level, _ = SafetyManager.evaluate("copy that")
        self.assertEqual(level, SafetyLevel.SAFE)

        # Sensitive
        level, _ = SafetyManager.evaluate("close all tabs")
        self.assertEqual(level, SafetyLevel.SENSITIVE)

        # Dangerous
        level, _ = SafetyManager.evaluate("delete folder projects")
        self.assertEqual(level, SafetyLevel.DANGEROUS)

        level, _ = SafetyManager.evaluate("format drive c:")
        self.assertEqual(level, SafetyLevel.DANGEROUS)

    def test_local_command_router(self):
        """Test fast zero-latency local matching."""
        res = command_router.match_local_command("copy that")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "copy_that")

        res = command_router.match_local_command("paste here")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "paste_that")

        res = command_router.match_local_command("click that")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "click_current")

        res = command_router.match_local_command("scroll down")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "scroll_down")

        res = command_router.match_local_command("open notepad")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "open_app")
        self.assertEqual(res["target"], "notepad")

        # Test command prompt with typos and laptop qualifiers
        res = command_router.match_local_command("opin command prompt in my loptop not crome")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "open_app")
        self.assertEqual(res["target"], "command prompt")

        # Test direct streaming portals with slang and typos
        res = command_router.match_local_command("opin jio hostar in that bigboss live")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "search_hotstar")
        self.assertIn("bigboss live", res["query"])

        res = command_router.match_local_command("opin telugu bigboss in the hostar season10")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "search_hotstar")
        self.assertIn("telugu bigboss", res["query"])

        # Test tab/window switching with user's exact phrase
        res = command_router.match_local_command("opin youtube that i have already keep opined in tha crome")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "focus_window")
        self.assertEqual(res["target"], "youtube")

        # Test copy screen content with typos
        res = command_router.match_local_command("coppy my current text screen content")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "copy_screen_text")

        # Test WhatsApp messaging and chat opening
        res = command_router.match_local_command("send whatsapp message to Rahul saying I am on my way")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "send_whatsapp_message")
        self.assertEqual(res["contact"], "rahul")
        self.assertEqual(res["message"], "i am on my way")

        res = command_router.match_local_command("open whatsapp search Priya")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "open_whatsapp_chat")
        self.assertEqual(res["contact"], "priya")

        # Test Terminal / Command Prompt task execution
        res = command_router.match_local_command("run command in cmd pip install fastapi")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "run_cmd")
        self.assertEqual(res["command"], "pip install fastapi")

        # Test step-by-step WhatsApp in-app commands
        res = command_router.match_local_command("open whatsapp app")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "open_browser")
        self.assertEqual(res["url"], "https://web.whatsapp.com")

        res = command_router.match_local_command("open whatsapp in that Rahul chat")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "open_whatsapp_chat")
        self.assertEqual(res["contact"], "rahul")

        res = command_router.match_local_command("in whatsapp open Alex")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "open_whatsapp_chat")
        self.assertEqual(res["contact"], "alex")

        res = command_router.match_local_command("type message hello how are you")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "type_text")
        self.assertEqual(res["text"], "hello how are you")

        res = command_router.match_local_command("click send button")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "press_key")
        self.assertEqual(res["key"], "enter")

        # Test YouTube granular tutorial search
        res = command_router.match_local_command("in youtube open Python tutorial")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "search_youtube")
        self.assertIn("python", res["query"])

        # Test Folder & Clipboard
        res = command_router.match_local_command("open this folder")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "open_folder")

        res = command_router.match_local_command("copy this content")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "copy_that")

        res = command_router.match_local_command("close tab")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "close_tab")

    def test_privacy_guard_sanitization(self):
        """Test password and secret redaction."""
        from safety.privacy_guard import privacy_guard
        clean = privacy_guard.sanitize_log("login with password=supersecret123 to portal")
        self.assertNotIn("supersecret123", clean)
        self.assertIn("password=********", clean)

    def test_task_planner_decomposition(self):
        """Test heuristic & complex planning."""
        # Complex YouTube query
        plan = task_planner.plan("open youtube and play python fast api tutorial")
        self.assertTrue(len(plan) > 0)
        self.assertEqual(plan[0]["action"], "search_youtube")
        self.assertIn("fast api", plan[0]["parameters"]["query"])

        # Multi-step: copy and paste
        plan = task_planner.plan("copy that and open notepad and paste it")
        self.assertEqual(len(plan), 3)
        self.assertEqual(plan[0]["action"], "copy_that")
        self.assertEqual(plan[1]["action"], "open_app")
        self.assertEqual(plan[2]["action"], "paste_that")

    def test_action_verifier(self):
        """Test verifier messages."""
        success, msg = action_verifier.verify("open_app", {"app_name": "notepad"})
        self.assertTrue(success)
        self.assertIn("Opened notepad", msg)


if __name__ == "__main__":
    unittest.main()
