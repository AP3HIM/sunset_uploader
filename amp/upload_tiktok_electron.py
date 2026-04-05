# upload_tiktok_electron.py
import pyautogui
import time
import os
import random
import pyperclip
import json

# -------------------
# Paths (unchanged)
# -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '../images')

SIGNALS_DIR = r"C:\Users\adipa\sunsetuploader\signals"
os.makedirs(SIGNALS_DIR, exist_ok=True)

# -------------------
# Configuration
# -------------------
SELECT_VIDEO_BOX = ((397, 325), (1827, 853))
CAPTION_FALLBACK = [
    (881, 641), (885, 645), (877, 637), (890, 641),
    (875, 643), (881, 635), (880, 648), (888, 638), (873, 646)
]

# -------------------
# Utilities
# -------------------

def write_tiktok_ready_signal(caption, video_file):
    payload = {
        "platform": "tiktok",
        "caption": caption,
        "video": video_file,
        "status": "READY",
        "timestamp": time.time()
    }

    signal_path = os.path.join(SIGNALS_DIR, "tiktok_ready.json")
    with open(signal_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    print(" TikTok ready signal written.")

def safe_locate(image_name, confidence=0.75, retries=15, delay=0.6):
    """Locate an image on screen with retries. Uses IMAGES_DIR/<image_name>."""
    img_path = os.path.join(IMAGES_DIR, image_name)
    for _ in range(retries):
        try:
            pt = pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
        except Exception:
            pt = None
        if pt:
            return pt
        time.sleep(delay)
    return None


def click_random_in_box(upper_left, bottom_right):
    x = random.randint(upper_left[0], bottom_right[0])
    y = random.randint(upper_left[1], bottom_right[1])
    pyautogui.click(x, y)
    return x, y


def write_caption(caption):
    """Click known caption area(s) and type."""
    for x, y in CAPTION_FALLBACK:
        try:
            pyautogui.click(x, y)
            time.sleep(0.4)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(caption, interval=0.05)
            print(f" Caption entered at ({x}, {y}).")
            return True
        except Exception:
            continue
    print(" Failed to write caption.")
    return False

def paste_file_path(video_file):
    """Paste path into Windows dialog more reliably with verification."""
    pyperclip.copy(video_file)
    for attempt in range(3):
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(0.8)
        # Heuristic: check if file dialog closed (screen changed)
        if not pyautogui.locateOnScreen(os.path.join(IMAGES_DIR, "select_file.png"), confidence=0.75):
            print(" File path pasted successfully.")
            return True
        print(f" Retry {attempt+1}: File dialog still open, trying again.")
    print(" Failed to close file dialog after pasting path.")
    return False


# -------------------
# Main Upload Logic
# -------------------
def upload(caption, video_file, paste_path_func=None):
    print(" Starting TikTok upload process...")
    time.sleep(4)

    # Step 1: Click Select video
    print(" Looking for 'Select video' button...")
    select_btn = safe_locate('select_file.png', confidence=0.75, retries=10, delay=0.5)
    if select_btn:
        pyautogui.click(select_btn)
        print(" Clicked 'Select video' by image.")
    else:
        print(" 'Select video' not found. Clicking inside known area...")
        click_random_in_box(*SELECT_VIDEO_BOX)

    # Step 2: Paste file path
    time.sleep(1)
    print(f" Pasting path: {video_file}")
    if paste_path_func:
        paste_path_func(video_file)
    else:   
        paste_file_path(video_file)

    # Step 3: Wait for caption box to appear
    time.sleep(3)
    print(" Writing caption...")
    write_caption(caption)

    write_tiktok_ready_signal(caption, video_file)
    print(" Handed off to DOM for Post.")
    print(" TikTok post completed successfully!")