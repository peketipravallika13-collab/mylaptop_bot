"""Interactive Terminal Assistant: Type commands directly and execute on demand."""
import sys
import os
import time
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from execution.task_executor import task_executor
from voice.text_to_speech import tts_engine


def flush_stdin():
    """Clear any buffered/pasted keystrokes on Windows."""
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except Exception:
        pass


def execute_typed_command(command_text: str):
    """Execute the user's typed command and show clear results."""
    print(f"\n[Processing]: \"{command_text}\"")
    
    success, message = task_executor.execute_command(command_text)
    
    status_label = "SUCCESS" if success else "FAILED"
    print(f"[{status_label}]: {message}")
    
    # Speak output response
    try:
        tts_engine.speak(message)
    except Exception:
        pass
    print("--------------------------------------------------")


def main():
    print("==================================================")
    print("   🤖 Personal AI Desktop Assistant (Terminal)")
    print("   Ready and waiting for your command.")
    print("==================================================")
    print("   Examples you can type:")
    print("   • open command prompt")
    print("   • open whatsapp")
    print("   • open youtube and play python tutorial")
    print("   • open hotstar and play bigboss live")
    print("   • open notepad and type hello world")
    print("   • copy that / paste that")
    print("   • close tab / switch to youtube tab")
    print("   • exit (to quit)")
    print("==================================================")

    # Flush any stale buffer
    flush_stdin()

    while True:
        try:
            # Sits and waits patiently for user to type
            user_input = input("\nWhat would you like me to do? > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("exit", "quit", "q", "bye"):
                print("Goodbye!")
                break

            execute_typed_command(user_input)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting assistant...")
            break


if __name__ == "__main__":
    main()
