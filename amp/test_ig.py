import time
import pyperclip
from upload_instagram_electron import upload_instagram

# 👇 Your test video and caption
VIDEO_PATH = r"C:\Users\adipa\OneDrive\Desktop\TikTokVideos\ptm_clips\1024.mp4"
CAPTION = "test video"

# Function to paste video path automatically
def paste_path(path):
    import pyautogui
    import pyperclip
    pyperclip.copy(path)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    pyautogui.press("enter")

print("\n--- Starting test upload ---\n")

upload_instagram(CAPTION, VIDEO_PATH, paste_path)

print("\n--- Upload finished ---\n")
