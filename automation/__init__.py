from .clipboard_manager import clipboard_mgr, ClipboardManager
from .keyboard_mouse import km_ctrl, KeyboardMouseController
from .windows_controller import win_ctrl, WindowsController
from .browser_controller import browser_ctrl, BrowserController
from .file_controller import file_ctrl, FileController
from .whatsapp_controller import whatsapp_ctrl, WhatsAppController
from .terminal_controller import terminal_ctrl, TerminalController

__all__ = [
    "clipboard_mgr", "ClipboardManager",
    "km_ctrl", "KeyboardMouseController",
    "win_ctrl", "WindowsController",
    "browser_ctrl", "BrowserController",
    "file_ctrl", "FileController",
    "whatsapp_ctrl", "WhatsAppController",
    "terminal_ctrl", "TerminalController"
]
