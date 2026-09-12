"""File and System Explorer Controller."""
import os
import subprocess
from pathlib import Path
from typing import Optional
from config.settings import KNOWN_FOLDERS, DEBUG


class FileController:
    """Controls opening folders, files, and safe filesystem operations."""

    @staticmethod
    def open_folder(folder_name_or_path: str) -> bool:
        """Open a directory in Windows File Explorer."""
        clean_name = folder_name_or_path.lower().strip()
        target_path = KNOWN_FOLDERS.get(clean_name, folder_name_or_path)

        path_obj = Path(target_path)
        if not path_obj.exists():
            # Try resolving relative or check if user specified a drive
            if DEBUG:
                print(f"[FileController] Path does not exist: {target_path}")
            return False

        try:
            if DEBUG:
                print(f"[FileController] Opening folder: {path_obj}")
            subprocess.Popen(f'explorer "{str(path_obj)}"', shell=True)
            return True
        except Exception as e:
            if DEBUG:
                print(f"[FileController Error] Opening folder: {e}")
            return False

    @staticmethod
    def open_file(file_path: str) -> bool:
        """Safely open a file with its default Windows application."""
        path_obj = Path(file_path)
        if not path_obj.exists() or not path_obj.is_file():
            return False
        try:
            os.startfile(str(path_obj))
            return True
        except Exception as e:
            if DEBUG:
                print(f"[FileController Error] Opening file: {e}")
            return False


file_ctrl = FileController()
