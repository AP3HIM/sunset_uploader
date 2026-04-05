import sys, os, time, platform, subprocess
import pyautogui

try:
    import pyperclip
except ImportError:
    pyperclip = None

def copy_to_clipboard(text):
    if pyperclip:
        pyperclip.copy(text)
        return True
    plat = platform.system()
    try:
        if plat == "Windows":
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            p.stdin.write(text.encode('utf-8'))
            p.stdin.close()
            return True
        elif plat == "Darwin":
            p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            p.stdin.write(text.encode('utf-8'))
            p.stdin.close()
            return True
        else:  # Linux
            p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            p.stdin.write(text.encode('utf-8'))
            p.stdin.close()
            return True
    except Exception:
        return False

def paste_path_and_confirm(abs_path):
    # Optional: save old clipboard
    try:
        old_clip = pyperclip.paste() if pyperclip else None
    except:
        old_clip = None

    ok = copy_to_clipboard(abs_path)
    time.sleep(0.25)
    if not ok:
        pyautogui.write(abs_path, interval=0.02)
    else:
        if platform.system() == 'Darwin':
            pyautogui.hotkey('command', 'v')
        else:
            pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.25)
    pyautogui.press('enter')

    # Restore clipboard
    if pyperclip and old_clip is not None:
        time.sleep(0.1)
        pyperclip.copy(old_clip)
    
    print(f"Copying to clipboard: {abs_path}")
    print(f"Clipboard copy success: {ok}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERR: No file path passed")
        sys.exit(1)

    abs_path = sys.argv[1]
    print(f"Pasting file path: {abs_path}")

    paste_path_and_confirm(abs_path)
    print("Done pasting path")
