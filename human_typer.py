# human_type_to_word.py
# Requirements: pip install pyautogui python-docx pyperclip keyboard pygetwindow

import pyautogui
import time
import random
import keyboard
import pygetwindow as gw    
import tkinter as tk
import ctypes
import pyperclip
from langdetect import detect, LangDetectException
from tkinter import filedialog
from pathlib import Path
from docx import Document   # only needed for .docx

# ================= CONFIG =================
BASE_DELAY       = 0.07       # ~170-180 wpm base speed
DELAY_VARIATION  = 0.035
TYPO_PROB        = 0.015      # ~1.5% chance per char
CORRECT_AFTER_TYPO_PROB = 0.95
BACKSPACE_DELAY  = 0.12
PAUSE_AFTER_WORD_PROB = 0.18
PAUSE_AFTER_WORD = 0.45       # thinking pause
BOLD_TRIGGER_PROB = 0.07      # chance to format a phrase when we see bold run

EMERGENCY_STOP   = 'ctrl+q'   # globally stop typing shortcut
PAUSE_PLAY_KEY   = 'ctrl+shift+p' # pause/resume typing
# ==========================================

is_running = True
is_paused = False

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print(f"\n[PAUSED] Press '{PAUSE_PLAY_KEY}' to resume typing.")
    else:
        print(f"\n[RESUMED] Resuming typing...")

def stop_typing():
    global is_running
    print(f"\n[{EMERGENCY_STOP}] pressed! Emergency stop requested.")
    is_running = False

def human_delay():
    return max(0.015, BASE_DELAY + random.uniform(-DELAY_VARIATION, DELAY_VARIATION))

def type_char(c):
    # If the character is a known dead-key that combines (like `"`,`'`,`~`,`^`,etc.)
    # we explicitly copy-paste it to avoid triggering the international keyboard layout combinator
    if c in "\"'~^`¨´":
        pyperclip.copy(c)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(human_delay() / 2)
    else:
        pyautogui.write(c, interval=human_delay() / 2)  # slightly faster per key feel

def maybe_typo_and_correct(char):
    if not char.isalpha() or random.random() > TYPO_PROB:
        type_char(char)
        return

    # Simulate realistic typo (neighbor key - very simplified)
    neighbors = {
        'a':['q','s','z','w', 'ش'], 's':['a','d','w','x','e', 'ث'],
        'd':['s','f','e','r'], 'f':['d','g','r','t'],
        'g':['f','h','t','y'], 'h':['g','j','y','u'],
        'j':['h','k','u','i'], 'k':['j','l','i','o'],
        'l':['k','o','p'],
    }.get(char.lower(), [chr(ord(char.lower()) + random.randint(-2,2))])

    wrong = random.choice(neighbors)
    if wrong == char.lower(): 
        type_char(char)
        return

    type_char(wrong)
    time.sleep(BACKSPACE_DELAY + random.uniform(0, 0.08))

    if random.random() < CORRECT_AFTER_TYPO_PROB:
        pyautogui.press('backspace')
        time.sleep(BACKSPACE_DELAY)
        type_char(char)
    # else: leave typo (realistic sometimes people miss)

def apply_bold(length):
    if length < 1: return
    # Select backwards
    for _ in range(length):
        pyautogui.hotkey('shift', 'left')
        time.sleep(0.04 + random.uniform(0, 0.07))
    pyautogui.hotkey('ctrl', 'b')
    time.sleep(0.25 + random.uniform(0, 0.35))
    # Return to end
    pyautogui.press('right', presses=length, interval=0.04)

def human_type_text(text_content, runs=None, target_app="Word"):
    global is_running, is_paused
    pyautogui.FAILSAFE = True
    
    # --- LANGUAGE DETECTION ---
    try:
        doc_lang = detect(text_content)
        print(f"\n[INFO] Detected Document Language: {doc_lang.upper()}")
    except LangDetectException:
        print("\n[INFO] Document language could not be confidently detected.")
        
    try:
        # Get active keyboard layout HEX (e.g. 0x00020409 = US-Intl, etc.)
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        klid = user32.GetKeyboardLayout(user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), 0))
        klid_hex = hex(klid & 0xFFFFFFFF)
        print(f"[INFO] Active Windows Keyboard Layout ID: {klid_hex}")
    except Exception:
        pass
    # ---------------------------

    print(f"\nStarting in 6 seconds... FOCUS {target_app} NOW!")
    print(f"-> Press '{PAUSE_PLAY_KEY}' to PAUSE / PLAY.")
    print(f"-> Press '{EMERGENCY_STOP}' at any time to abort the process.")
    
    keyboard.add_hotkey(EMERGENCY_STOP, stop_typing)
    keyboard.add_hotkey(PAUSE_PLAY_KEY, toggle_pause)
    time.sleep(6)

    i = 0
    bold_stack = {}  # positions where bold starts/ends if using runs

    while i < len(text_content):
        if not is_running:
            print("Finished (Stopped by user).")
            return
            
        while is_paused and is_running:
            time.sleep(0.5)
            
        if not is_running: 
            return # Extra check inside the pause loop
            
        try:
            active_window = gw.getActiveWindow()
            if active_window is None or target_app not in active_window.title:
                print(f"'{target_app}' is not focused! Pausing... (Please focus '{target_app}'!)")
                time.sleep(1)
                continue
        except Exception:
            pass # In case pygetwindow fails (e.g. non-Windows OS)

        char = text_content[i]

        # Word-end pause
        if char.isspace() and random.random() < PAUSE_AFTER_WORD_PROB:
            time.sleep(PAUSE_AFTER_WORD + random.uniform(-0.2, 0.3))

        maybe_typo_and_correct(char)

        # Very rough bold simulation when we have formatting info
        if runs and i in bold_stack:
            phrase_len = bold_stack[i]
            apply_bold(phrase_len)
            del bold_stack[i]  # one time

        i += 1

    print("Finished.")

# ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Hide the main window
    
    # --- Choose Target App Dialog ---
    app_choice = ["Word"] # default fallback
    
    dialog = tk.Toplevel(root)
    dialog.title("Select Target Application")
    dialog.geometry("380x230")
    dialog.attributes('-topmost', True)
    
    tk.Label(dialog, text="Where do you want to type?", font=("Arial", 10, "bold")).pack(pady=10)
    
    var = tk.StringVar(value="Word")
    
    tk.Radiobutton(dialog, text="Microsoft Word", variable=var, value="Word").pack(anchor='w', padx=40)
    tk.Radiobutton(dialog, text="Google Docs (Browser)", variable=var, value="Docs").pack(anchor='w', padx=40)
    tk.Radiobutton(dialog, text="Notepad", variable=var, value="Notepad").pack(anchor='w', padx=40)
    
    custom_frame = tk.Frame(dialog)
    custom_frame.pack(anchor='w', padx=40, pady=5, fill='x')
    tk.Radiobutton(custom_frame, text="Other (Window title keyword):", variable=var, value="Other").pack(side='left')
    custom_entry = tk.Entry(custom_frame, width=15)
    custom_entry.pack(side='left', padx=5)
    
    def on_submit():
        if var.get() == "Other":
            app_choice[0] = custom_entry.get().strip() or "Word"
        else:
            app_choice[0] = var.get()
        dialog.destroy()
        
    tk.Button(dialog, text="OK", command=on_submit, width=10).pack(pady=10)
    
    def on_close():
        dialog.destroy()
        exit(0)
        
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    dialog.grab_set()
    dialog.wait_window()
    
    target_app = app_choice[0]
    print(f"Target application set to: {target_app}")
    # ---------------------------------
    
    root.attributes('-topmost', True) # Bring the file dialog to the front
    print("Please select a .txt or .docx file from the dialog...")
    path = filedialog.askopenfilename(
        title="Select a file to type",
        filetypes=[("Text and Word Documents", "*.txt;*.docx"), ("All Files", "*.*")]
    )

    if not path:
        print("No file selected. Exiting.")
        exit(0)

    p = Path(path)
    if not p.is_file():
        print("File not found.")
        exit(1)

    text = ""
    formatting_runs = None  # list of (start_index, length) for bold

    if p.suffix.lower() == '.docx':
        try:
            doc = Document(p)
            full_text = []
            bold_positions = []
            current_pos = 0

            for para in doc.paragraphs:
                for run in para.runs:
                    run_text = run.text
                    if not run_text: continue

                    is_bold = run.bold or run.font.bold  # sometimes in font

                    full_text.append(run_text)
                    if is_bold and run_text.strip():
                        bold_positions.append((current_pos, len(run_text)))

                    current_pos += len(run_text)

                full_text.append('\n')  # paragraph break
                current_pos += 1

            text = ''.join(full_text).rstrip()
            # Convert bold runs to char-index → length map for typing
            formatting_runs = {}
            for start, length in bold_positions:
                formatting_runs[start] = length

        except Exception as e:
            print(f"Error reading .docx: {e}")
            text = p.read_text(encoding='utf-8', errors='replace')

    else:  # .txt or anything else
        text = p.read_text(encoding='utf-8', errors='replace')

    # For .odt / webpage → convert manually to .docx or .txt first

    print(f"Loaded {len(text)} characters.")
    human_type_text(text, formatting_runs, target_app)