# Human Typer

This project simulates realistic human typing into Microsoft Word (or any text editor) with simulated typos, correcting mistakes, formatting bold text, and pausing between words.

## Features
- **Realistic Typing Speed**: Types characters with human-like delays and variances.
- **Typo Simulation**: Occasionally mistypes using adjacent keys and realistically backspaces to correct it.
- **Bold Text formatting**: Automatically simulates selecting and pushing `CTRL+B` to bold text (works natively with `.docx` reading).
- **Auto-Pause on Defocus**: Automatically detects if Microsoft Word loses focus and pauses typing until it is selected again.
- **GUI File Selection**: Native Windows dialog to browse and select files rather than copying paths.
- **Language Detection**: Automatically detects the text document's language and extracts the active Windows Keyboard Layout ID.
- **Dead-Key Safe Typing**: Automatically detects keys that would normally combine in international layouts (like `"` or `~`) and pastes them instead to prevent broken sequences.
- **Pause & Resume**: Press `CTRL+SHIFT+P` to pause typing instantly and resume when ready.
- **Emergency Stop**: Press `CTRL+Q` to stop the script at any time during execution.

## Requirements
- Python 3.10+
- OS: Windows (required for PyGetWindow to detect Microsoft Word's focus)

## Installation

1. Clone the repository.
2. Install the required dependencies:
   ```bash   pip install -r requirements.txt   ```

### Docker
A simple Dockerfile is provided to containerize the environment. However, because this application interacts with a GUI desktop environment (Microsoft Word) and reads keyboard inputs globally, **running it inside a standard Docker Linux container will encounter GUI limitations**. 

To build:
```bashdocker build -t human_typer .```

To run it properly, it's highly recommended to run natively on the Windows host.

## Usage
Run the script natively:
```bash
python human_typer.py
```
1. A file browser dialog will pop up. Select your `.txt` or `.docx` file.
2. The script logs the detected language and keyboard layout to the console, then waits 6 seconds before starting. Focus the Microsoft Word window during this time.
3. To pause or resume typing, press `CTRL+SHIFT+P`.
4. To abort typing at any moment completely, press `CTRL+Q`.
