# Human Typer - Developer & AI Documentation

## Core Purpose
The `human_typer.py` script mimics authentic human keyboard typing interactions from pre-existing text files (`.txt.`, `.docx`). 

## Technical Architecture
- **GUI Control (`pyautogui`)**: Manages the keystrokes.
- **Global Hooks (`keyboard`)**: Listens to hotkeys globally (`CTRL+Q` to abort, `CTRL+SHIFT+P` to pause).
- **Active Window State (`pygetwindow`)**: Used to ensure the keys are only being sent to the target application ("Word" by default). Because this hook is Windows-only natively, ensure proper handling when adapting or testing for MacOS/Linux (a try-except block is in place for cross-platform fallback, though it skips the focus verification).
- **Dead-Key bypass (`pyperclip`)**: International layouts interpret some characters (like `~`, `'`, `"`) as combinators. Typing `"i` via OS-level emulation transforms into `ï`. We bypass this by specifically pasting `pyperclip.copy(char)` -> `CTRL+V` for dead key characters instead of pressing them via `pyautogui`.
- **System Information (`ctypes` & `langdetect`)**: The script checks the document language using `langdetect`, and checks the active Windows Hex Keyboard Layout (`GetKeyboardLayout` via `ctypes.WinDLL`) to provide context to the user if characters misalign due to system layout mismatches.
- **DOCX Parsing (`python-docx`)**: Used to retain formatting (like bold text index tracking).
- **File Dialog (`tkinter`)**: Used to spawn a native GUI prompt for selecting the target document without relying on console input strings.

## Development Notes
- **Extending features**: To add italics or underline formatting, mirror the `apply_bold` logic but replace the hotkey sequence. Update the tuple logic `(start_index, length)` tracking runs.
- **Typo System**: `maybe_typo_and_correct` currently only contains nearby keys for a few character mappings (`a`, `s`, etc). It falls back to character shifting for undefined keys. Expand the `neighbors` dictionary to fully model a qwerty keyboard layout for more realistic outcomes.
- **Dockerization Limitations**: Since GUI scripts require an X-server or native Windows GUI, the included `Dockerfile` functions as a dependency bundler rather than a complete ready-to-run daemon. If GUI functionality needs to be Dockerized strictly, look into X11 socket sharing (`-v /tmp/.X11-unix:/tmp/.X11-unix`) or a dedicated Windows desktop container.
