from upload_instagram_electron import upload_instagram, DRY_RUN, diagnose_images
import pyperclip
import time

# optional: toggle dry run
# from upload_instagram_electron import DRY_RUN
# DRY_RUN = True

VIDEO_PATH = r"C:\Users\adipa\OneDrive\Desktop\TikTokVideos\ptm_clips\1024.mp4"
CAPTION = "test video"

def paste_path(path):
    # Use clipboard then ctrl-v+enter — generally reliable on Windows
    pyperclip.copy(path)
    time.sleep(0.2)
    pyperclip.paste()  # no-op but keeps debugger happy
    import pyautogui
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')

# Optionally see what images are currently detectable
diagnose_images()

# Now call upload (set DRY_RUN = False to actually click)
success = upload_instagram(CAPTION, VIDEO_PATH, paste_path)
print("Upload result:", success)
