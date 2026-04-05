# amp/upload_tiktok_electron.py
import pyautogui
import time
import os
import random
import pyperclip
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '../images')

SIGNALS_DIR = r"C:\Users\adipa\sunsetuploader\signals"
os.makedirs(SIGNALS_DIR, exist_ok=True)

# ── Post button config ────────────────────────────────────────────────────────
POST_BUTTON_COORDS = [
    (357, 1009),
    (474, 1006),
    (586, 1008),
]
POST_BUTTON_COLOR     = (254, 44, 85)
POST_BUTTON_TOLERANCE = 15

# ── File select config ────────────────────────────────────────────────────────
SELECT_VIDEO_BOX = ((397, 325), (1827, 853))
CAPTION_FALLBACK = [
    (881, 641), (885, 645), (877, 637), (890, 641),
    (875, 643), (881, 635), (880, 648), (888, 638), (873, 646)
]


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def safe_locate(image_name, confidence=0.75, retries=15, delay=0.6):
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


def paste_file_path(video_file):
    pyperclip.copy(video_file)
    for attempt in range(3):
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(0.8)
        if not pyautogui.locateOnScreen(
            os.path.join(IMAGES_DIR, "select_file.png"), confidence=0.75
        ):
            print("File path pasted successfully.")
            return True
        print(f"Retry {attempt+1}: file dialog still open.")
    print("Failed to close file dialog.")
    return False


def strong_click(x, y):
    """Human-like precise click."""
    pyautogui.moveTo(x, y, duration=0.05)
    pyautogui.mouseDown()
    time.sleep(0.05)
    pyautogui.mouseUp()


def click_wave(coords_list, label, repeat_per_coord=3, wait=0.15):
    print(f"  [{label}] Clicking {len(coords_list)} coords x{repeat_per_coord}...")
    for (cx, cy) in coords_list:
        for _ in range(repeat_per_coord):
            jx = cx + random.randint(-4, 4)
            jy = cy + random.randint(-3, 3)
            strong_click(jx, jy)
            time.sleep(wait)


# ─────────────────────────────────────────────────────────────────────────────
# PAG: File selection (this step DOM cannot do — native OS dialog)
# ─────────────────────────────────────────────────────────────────────────────

def select_file_only(video_file, paste_path_func=None):
    """
    Called in hybrid mode: Electron opened the window, PAG just selects the file.
    DOM takes over for caption and post after this returns.
    """
    print("PAG: Looking for Select Video button...")
    time.sleep(2)

    select_btn = safe_locate('select_file.png', confidence=0.75, retries=10, delay=0.5)
    if select_btn:
        pyautogui.click(select_btn)
        print("PAG: Clicked Select Video by image match.")
    else:
        print("PAG: Image not found, clicking known area.")
        click_random_in_box(*SELECT_VIDEO_BOX)

    time.sleep(1)
    print(f"PAG: Pasting file path: {video_file}")
    if paste_path_func:
        paste_path_func(video_file)
    else:
        paste_file_path(video_file)

    print("PAG: File selection done. Handing off to DOM.")


# ─────────────────────────────────────────────────────────────────────────────
# PAG: Caption fallback (only if DOM caption injection fails)
# ─────────────────────────────────────────────────────────────────────────────

def write_caption_pag(caption):
    """PAG fallback for caption — tries known coordinates."""
    print("PAG: Attempting caption via coordinate fallback...")
    for x, y in CAPTION_FALLBACK:
        try:
            pyautogui.click(x, y)
            time.sleep(0.4)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(caption, interval=0.05)
            print(f"PAG: Caption entered at ({x}, {y}).")
            return True
        except Exception:
            continue
    print("PAG: Caption fallback failed.")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# PAG: Three-stage Post button detection
# Called when DOM fails to click Post
# ─────────────────────────────────────────────────────────────────────────────

def wait_for_post_button(max_wait=180, check_interval=2):
    """
    Three-stage Post button detection:
      Stage 1 — RGB color check (most reliable, button turns red when ready)
      Stage 2 — Image match (post_file.png)
      Stage 3 — Coordinate sweep fallback
    """
    print("PAG: Waiting for Post button...")
    start = time.time()
    post_img_path = os.path.join(IMAGES_DIR, "post_file.png")

    while time.time() - start < max_wait:
        # Stage 1: RGB color check
        try:
            pixel = pyautogui.screenshot().getpixel(POST_BUTTON_COORDS[1])
        except Exception as e:
            print(f"PAG: Screenshot error: {e}")
            pixel = None

        if pixel and all(
            abs(pixel[i] - POST_BUTTON_COLOR[i]) <= POST_BUTTON_TOLERANCE
            for i in range(3)
        ):
            print(f"PAG: [Stage 1] RGB confirmed red button (color={pixel}). Clicking...")
            click_wave(POST_BUTTON_COORDS, "RGB Confirmed", repeat_per_coord=3, wait=0.15)
            return True

        time.sleep(3)

        # Stage 2: Image match
        try:
            btn_loc = pyautogui.locateCenterOnScreen(post_img_path, confidence=0.75)
        except Exception:
            btn_loc = None

        if btn_loc:
            print(f"PAG: [Stage 2] Image match at {btn_loc}. Clicking...")
            for _ in range(4):
                jx = btn_loc[0] + random.randint(-3, 3)
                jy = btn_loc[1] + random.randint(-3, 3)
                strong_click(jx, jy)
                time.sleep(0.15)
            return True

        # Stage 3: Coordinate sweep
        print("PAG: [Stage 3] No RGB or image match. Forcing coordinate sweep...")
        click_wave(POST_BUTTON_COORDS, "Fallback Sweep", repeat_per_coord=2, wait=0.25)
        pyautogui.scroll(-600)
        time.sleep(check_interval)

    # Final failsafe
    print("PAG: Timeout reached. Running final failsafe click wave...")
    click_wave(POST_BUTTON_COORDS, "Failsafe", repeat_per_coord=4, wait=0.2)
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Signal file (kept for legacy Chrome extension flow)
# ─────────────────────────────────────────────────────────────────────────────

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
    print("TikTok ready signal written.")


# ─────────────────────────────────────────────────────────────────────────────
# Main upload function
# dom_success_caption and dom_success_post are passed in from the Electron
# renderer after it attempts DOM injection — True means DOM handled it,
# False means PAG fallback is needed.
# ─────────────────────────────────────────────────────────────────────────────

def upload(
    caption,
    video_file,
    paste_path_func=None,
    dom_success_caption=False,
    dom_success_post=False,
):
    """
    Hybrid TikTok upload.

    Flow:
      1. PAG selects the file (DOM cannot touch native OS dialogs)
      2. DOM attempts caption injection (handled in Electron renderer)
         → if dom_success_caption=False, PAG fallback fires here
      3. DOM attempts to click Post (handled in Electron renderer)
         → if dom_success_post=False, PAG three-stage post detection fires here

    When called from the old full-PAG path (upload.py mode='full'),
    both dom flags are False so PAG handles everything as before.
    """
    print("Starting TikTok upload process...")
    time.sleep(4)

    # ── Step 1: File selection (always PAG) ───────────────────────────────────
    print("Looking for 'Select video' button...")
    select_btn = safe_locate('select_file.png', confidence=0.75, retries=10, delay=0.5)
    if select_btn:
        pyautogui.click(select_btn)
        print("Clicked 'Select video' by image.")
    else:
        print("'Select video' not found. Clicking inside known area...")
        click_random_in_box(*SELECT_VIDEO_BOX)

    time.sleep(1)
    print(f"Pasting path: {video_file}")
    if paste_path_func:
        paste_path_func(video_file)
    else:
        paste_file_path(video_file)

    # ── Step 2: Caption ───────────────────────────────────────────────────────
    time.sleep(3)
    if dom_success_caption:
        print("Caption already handled by DOM. Skipping PAG caption.")
    else:
        print("DOM caption failed or not attempted. Running PAG caption fallback...")
        write_caption_pag(caption)

    # ── Step 3: Post ──────────────────────────────────────────────────────────
    if dom_success_post:
        print("Post already handled by DOM. Skipping PAG post.")
    else:
        print("DOM post failed or not attempted. Running PAG post fallback...")
        print("Scrolling down to Post button...")
        pyautogui.scroll(-10000)
        time.sleep(0.5)
        wait_for_post_button()

    # Signal file for legacy Chrome extension flow
    write_tiktok_ready_signal(caption, video_file)
    print("TikTok upload complete!")