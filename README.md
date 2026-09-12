# 🎙️ Personal AI Desktop Assistant

A modular, privacy-conscious, and agentic **Personal AI Desktop Assistant** running in the Windows System Tray. It provides seamless voice and hotkey-driven computer automation for browser navigation (YouTube, Google, tabs), desktop applications (VS Code, Notepad, Explorer, Terminal), clipboard operations (*"copy that"*, *"paste that"*), mouse clicks, and window management.

---

## 🌟 Architecture & Highlights

```
                    🟢 Windows System Tray / Hotkey (Ctrl+Alt+A)
                                      │
                                      ▼
                             🎤 Voice Listener
                                      │
                                      ▼
                            Speech-to-Text (STT)
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   Hybrid Command Router   │
                        └─────────────┬─────────────┘
                                      │
                     ┌────────────────┴────────────────┐
                     ▼                                 ▼
             ⚡ Fast Local Engine               🤖 AI Task Planner
             (0ms API Latency)                (Multi-step Reasoning)
                     │                                 │
                     └────────────────┬────────────────┘
                                      │
                                      ▼
                            🛡️ Safety & Permission
                        (Safe / Sensitive / Dangerous)
                                      │
                                      ▼
                            ⚙️ Action Executor
              (Browser / YouTube / Windows / Mouse / Clipboard)
                                      │
                                      ▼
                          🔍 Result Verification
                                      │
                                      ▼
                      🔊 Voice TTS + 🖥️ Desktop HUD
```

---

## 🚀 Key Features

1. **System Tray Integration**:
   - Right-click tray icon to **Start/Stop Voice**, trigger quick browser/clipboard shortcuts, inspect **Command History**, or view help.
   - Dynamic icon states (Mint green dot when listening, slate gray when idle).

2. **Hybrid Command Engine**:
   - **Zero-Latency Local Engine**: Instantly executes common desktop commands (*"copy that"*, *"paste that"*, *"open notepad"*, *"close tab"*, *"scroll down"*, *"pause"*, *"stop listening"*) without API latency or network dependency.
   - **AI Task Planner**: Decomposes complex natural language (*"Open YouTube and play Python FastAPI tutorial"*, *"Open VS Code and launch backend"*) into structured executable action plans.

3. **Desktop Automation Capabilities**:
   - **Browser & YouTube**: Direct search, auto-play first video, open tabs, switch tabs, close tabs.
   - **Windows Applications**: Launch VS Code, Notepad, Terminal, Calculator, File Explorer, Task Manager.
   - **Mouse & Keyboard**: Click current position, double click, right click, scroll up/down, hotkeys (`Win+D`, `Alt+F4`, `Ctrl+W`, `Ctrl+T`).
   - **Clipboard Context**: *"Copy that"* (stores selected text into context) and *"Paste that"*.

4. **Safety & Permission Manager**:
   - 🟢 **Safe**: Auto-executes standard safe tasks.
   - 🟡 **Sensitive**: Asks user confirmation for actions like closing all tabs or sending external requests.
   - 🔴 **Dangerous**: Blocks or requires explicit dialog confirmation for destructive operations (e.g. deleting directories).

5. **Desktop HUD & Feedback**:
   - Floating dark-mode HUD widget showing real-time state (`🎤 Listening...`, `⚡ Thinking...`, `✅ Done`, `⏸️ Paused`).
   - Non-blocking offline Text-to-Speech (`pyttsx3`).

6. **Persistent SQLite Memory**:
   - Stores timestamps, commands, status, and execution duration for audit and history review.

---

## 🛠️ Installation & Setup

### 1. Requirements
- Python 3.9+ on Windows
- Working microphone and audio output

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure AI Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your `GEMINI_API_KEY` for LLM-powered multi-step planning (or leave empty to use the built-in smart local heuristic planner).

---

## 🎮 Running the Assistant

Start the assistant:
```bash
python main.py
```

### Controls:
- **Global Hotkey**: Press `Ctrl+Alt+A` anywhere to start/stop listening.
- **System Tray**: Right-click the assistant icon in the bottom-right taskbar tray and click **🎤 Start Voice Listener**.

### Example Voice Commands:
- *"Open YouTube and play Python FastAPI tutorial"*
- *"Open browser"* / *"Open Google"*
- *"Copy that"*
- *"Open Notepad"*
- *"Paste that"*
- *"Click that"* / *"Double click"*
- *"Scroll down"* / *"Scroll up"*
- *"Close this tab"*
- *"Minimize window"* / *"Show desktop"*
- *"Open Downloads folder"*
- *"Stop listening"*
