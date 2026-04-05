# upload_instagram_electron.py
import pyautogui
import time
import os
import traceback
from typing import Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "../images")

# === CONFIG ===
DEFAULT_RETRIES = 4
DEFAULT_DELAY = 0.6
DEFAULT_CONFIDENCE = 0.8
FILE_DIALOG_TIMEOUT = 8  # seconds
DRY_RUN = False  # set True for testing (no clicks, just logs)

# Coordinates you already rely on as fallbacks (leave them)
FALLBACKS = {
    "create": (41, 770),
    "new_post": (121, 791),
    "select_file": (945, 757),
    "next1": (1271, 289),
    "next2": (1482, 284),
    "caption": (1285, 491),
    "share": (1479, 285),
}


def _log(*args, **kwargs):
    print("[IG-UPLOAD]", *args, **kwargs)


def img_path(image_name: str) -> str:
    return os.path.join(IMAGES_DIR, image_name)


def safe_locate(image_name: str, confidence=DEFAULT_CONFIDENCE,
                retries=DEFAULT_RETRIES, delay=DEFAULT_DELAY) -> Optional[pyautogui.Point]:
    """
    Try to locate an image on the screen with retries. Returns center Point or None.
    """
    path = img_path(image_name)
    for i in range(retries):
        try:
            loc = pyautogui.locateCenterOnScreen(path, confidence=confidence)
        except Exception as e:
            loc = None
            _log(f" safe_locate exception for {image_name}: {e}")
        if loc:
            _log(f"  found {image_name} @ {loc} (attempt {i+1})")
            return loc
        time.sleep(delay)
    _log(f"  did not find {image_name} (searched {retries}x)")
    return None


def click_point(pt: Tuple[int, int]):
    if DRY_RUN:
        _log(f" DRY RUN click @ {pt}")
        return
    pyautogui.click(pt)


def click_or_fallback(image_name: str, fallback_coords: Optional[Tuple[int, int]] = None,
                      retries=DEFAULT_RETRIES, delay=DEFAULT_DELAY, confidence=DEFAULT_CONFIDENCE) -> bool:
    """
    Click the image if found, otherwise click fallback coords.
    Returns True if clicked, False otherwise.
    """
    loc = safe_locate(image_name, confidence=confidence, retries=retries, delay=delay)
    if loc:
        click_point((loc.x, loc.y))
        _log(f" Clicked image {image_name} at {loc}")
        return True
    if fallback_coords:
        click_point(fallback_coords)
        _log(f" Fallback click {image_name} at {fallback_coords}")
        return True
    _log(f" No image or fallback for {image_name}")
    return False


def hover_then_find(image_name: str, hover_coords: Tuple[int, int],
                    confidence=DEFAULT_CONFIDENCE, retries=3, delay=0.2) -> Optional[pyautogui.Point]:
    """
    Move the mouse to hover_coords to trigger any hover-expansion UI, then attempt to locate image.
    Useful for the plus -> expanded "+ Create" behavior.
    """
    _log(f" Hovering at {hover_coords} to reveal {image_name}")
    if not DRY_RUN:
        pyautogui.moveTo(hover_coords[0], hover_coords[1], duration=0.12)
        time.sleep(0.18)
    # After hover, try to locate the more specific image
    return safe_locate(image_name, confidence=confidence, retries=retries, delay=delay)


def wait_for_file_dialog_close(video_file: str, paste_path_func, max_wait=FILE_DIALOG_TIMEOUT) -> bool:
    """
    Expectation:
      - The code that opens the OS file dialog should call this AFTER the dialog is open.
      - This function will call the provided paste_path_func exactly ONCE, which should:
          - paste or type the full filepath into the dialog, and
          - press Enter once to confirm.
      - Then this function waits until the upload dialog disappears OR the 'Next' button is present.
    Important:
      - DO NOT press Enter twice here (this was causing the media player to open on some machines).
      - The paste_path_func must paste via clipboard (ctrl+v) then press enter ONCE.
    """
    start = time.time()

    # Call the external paste function (should paste path + press Enter once)
    try:
        _log("Calling paste_path_func to paste file path into file dialog...")
        paste_path_func(video_file)
        _log("paste_path_func returned — waiting for dialog to react.")
    except Exception as e:
        _log(f" Error calling paste_path_func: {e}")

    # short wait for dialog to respond
    time.sleep(0.6)

    # Poll until either 'Next' appears or 'Select file' disappears (meaning dialog closed/advanced)
    while time.time() - start < max_wait:
        next_btn = safe_locate('insta_next_file.png', confidence=0.70, retries=1, delay=0.25)
        select_btn = safe_locate('insta_select_file.png', confidence=0.72, retries=1, delay=0.25)
        if next_btn:
            _log("  Detected 'Next' -> dialog closed / progressed.")
            return True
        if not select_btn:
            _log("  'Select file' button gone -> dialog closed.")
            return True
        time.sleep(0.35)

    # Timeout fallback: send ESC once and re-check
    _log("  File dialog still present after timeout; sending ESC and re-checking.")
    if not DRY_RUN:
        pyautogui.press("esc")
        time.sleep(0.5)
    select_btn = safe_locate('insta_select_file.png', confidence=0.72, retries=1, delay=0.25)
    if not select_btn:
        _log("  Dialog gone after ESC.")
        return True
    _log("  Dialog still present after ESC.")
    return False


def diagnose_images(image_list=None):
    """
    Utility to check which images in images/ are detectable on-screen right now.
    Prints results. Useful for debugging which screenshots are busted.
    """
    if image_list is None:
        # default list: common images used
        image_list = [
            "insta_new_create_button.png",
            "insta_create_button.png",
            "new_ig_post_btn.png",
            "insta_select_file.png",
            "insta_next_file.png",
            "insta_caption_new.png",
            "insta_share_file.png",
        ]
    results = {}
    _log("Running diagnose_images() - will attempt quick locate for each image")
    for img in image_list:
        found = safe_locate(img, retries=2, delay=0.2, confidence=0.75)
        results[img] = bool(found)
        _log(f"  {img}: {'FOUND' if found else 'MISSING'}")
    return results


def try_click_post_or_skip() -> bool:
    """
    Attempt to click the "Post" option if it exists. If the Post option is not present,
    check if the select-file UI is already visible - if so, skip and return True.
    If neither found, finally click fallback coords (last resort).
    Returns True if we either clicked Post, skipped because select-file is visible, or used fallback.
    Returns False only if none of the above works (very unlikely).
    """
    # 1) try to find image for the "Post" option (do NOT click fallback immediately)
    post_loc = safe_locate("new_ig_post_btn.png", confidence=0.78, retries=2, delay=0.25)
    if post_loc:
        click_point((post_loc.x, post_loc.y))
        _log("Clicked 'Post' (image).")
        return True

    # 2) If Post image not found, maybe UI already jumped straight to select-file — check that
    select_loc = safe_locate("insta_select_file.png", confidence=0.75, retries=2, delay=0.25)
    if select_loc:
        _log("No 'Post' option found but select-file is already visible — continuing.")
        return True

    # 3) As last resort, click fallback coords for post choice (this is the risky fallback)
    _log("Neither 'Post' nor 'Select file' detected — falling back to coords to try to pick 'Post'.")
    click_point(FALLBACKS["new_post"])
    time.sleep(0.45)
    # After clicking fallback, check if select-file appeared (confirm)
    select_loc_after = safe_locate("insta_select_file.png", confidence=0.72, retries=2, delay=0.35)
    if select_loc_after:
        _log("Select-file appeared after fallback click.")
        return True

    _log("Fallback click did not produce select-file UI.")
    return False


def upload_instagram(caption: str, video_file: str, paste_path_func) -> bool:
    """
    Main sequence — preserves your original flow but adds robustness and checks.
    Returns True on attempted post (clicked share), False on abort.
    """
    try:
        _log("START Instagram upload sequence")
        # 1) Try hover+click create (handles the '+' -> expand UI)
        create_loc = hover_then_find("insta_new_create_button.png", hover_coords=FALLBACKS["create"])
        if create_loc:
            click_point((create_loc.x, create_loc.y))
            _log(" Clicked insta_new_create_button.png after hover.")
        else:
            # fallback to older create image or fallback coords
            clicked = click_or_fallback("insta_create_button.png", FALLBACKS["create"])
            if not clicked:
                _log("Could not open create menu, aborting.")
                return False
        time.sleep(0.6)

        # 2) --- improved logic here: try to click Post, but DON'T abort if the Post image isn't present ---
        if not try_click_post_or_skip():
            _log("Could not select 'Post' or detect select-file UI — aborting.")
            return False
        time.sleep(0.6)

        # 3) Click select file (image first, fallback coords)
        if not click_or_fallback("insta_select_file.png", FALLBACKS["select_file"]):
            _log("Could not click select file — aborting.")
            return False

        _log("Calling paste_path_func to paste the path into OS dialog...")
        # IMPORTANT: paste_path_func MUST paste via clipboard and press Enter once.
        paste_path_func(video_file)

        # 4) Wait for file dialog to close / for Next button to appear
        ok = wait_for_file_dialog_close(video_file, paste_path_func, max_wait=FILE_DIALOG_TIMEOUT)
        if not ok:
            _log("File dialog did not close / upload not accepted — aborting.")
            return False
        _log("File appears accepted.")

        # 5) Click Next twice (two-step IG flow)
        if not click_or_fallback("insta_next_file.png", FALLBACKS["next1"]):
            _log("Missing first Next — abort.")
            return False
        time.sleep(0.6)
        # Try second next (may be same image/button)
        if not click_or_fallback("insta_next_file.png", FALLBACKS["next2"]):
            _log("Missing second Next — abort.")
            return False
        time.sleep(0.6)

        # 6) Caption
        if not click_or_fallback("insta_caption_new.png", FALLBACKS["caption"]):
            _log("Caption box not found; will attempt keyboard fallback.")
            # fallback: tab then write
            if not DRY_RUN:
                pyautogui.hotkey("tab")
                time.sleep(0.15)
                pyautogui.typewrite(caption, interval=0.03)
        else:
            if not DRY_RUN:
                pyautogui.write(caption, interval=0.03)
        time.sleep(0.4)
        pyautogui.scroll(-800)
        time.sleep(0.6)

        # 7) Share
        if not click_or_fallback("insta_share_file.png", FALLBACKS["share"]):
            _log("Could not find Share button — aborting.")
            return False

        _log("Clicked Share — upload attempted.")
        return True

    except Exception:
        _log("Unhandled exception in upload_instagram:")
        traceback.print_exc()
        return False


# ---------------------------
# Recommended helper for pasting file path (use this or your working function)
# ---------------------------
def default_paste_path(video_file: str):
    """
    Copies path into clipboard and pastes it in the active file dialog, then presses Enter ONCE.
    This is the behavior that previously worked for you (avoid typing, avoid double-enter).
    Requires 'pyperclip' package installed in the environment.
    """
    try:
        import pyperclip
    except Exception:
        _log("pyperclip not available, falling back to typing the path (less reliable).")
        pyperclip = None

    if pyperclip:
        pyperclip.copy(video_file)
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.12)
        pyautogui.press("enter")
        _log("default_paste_path: pasted via clipboard and pressed Enter once.")
    else:
        # fallback typing (slower but works if pyperclip missing)
        pyautogui.typewrite(video_file, interval=0.004)
        time.sleep(0.05)
        pyautogui.press("enter")
        _log("default_paste_path: typed path and pressed Enter once.")


# If run directly, run a small self-test (dry-run by default)
if __name__ == "__main__":
    print("Running as script. DRY_RUN:", DRY_RUN)
    diagnose_images()
