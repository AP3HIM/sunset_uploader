import pyautogui
import time
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')

def get_featured_urls():
    base_url = "https://papertigercinema.com/movies/"
    with open(os.path.join(BASE_DIR, "featured_slugs.txt")) as f:
        slugs = [line.strip() for line in f if line.strip()]
    return [base_url + slug for slug in slugs]

def get_movie_title_from_url(url):
    return url.rstrip("/").split("/")[-1].replace("-", " ").title()

def safe_locate_center(image_name, confidence=0.8):
    try:
        return pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, image_name), confidence=confidence)
    except:
        return None
# handles error if DOM and react player/ video.js don't load immediately
def refresh_browser_tab(retries=2):
    for i in range(retries):
        print(f" Refreshing browser tab ({i+1}/{retries})...")
        pyautogui.hotkey('ctrl', 'r')
        time.sleep(10)
        video_area = safe_locate_center("video_player.png", confidence=0.8)
        if video_area:
            return video_area
    return None


def automate_ptc_movie(url=None, timestamp=0):
    print(f" Automating playback for current page: {url or 'unknown'}")

    # Reset scroll to top
    print(" Scrolling up repeatedly to reset layout...")
    for _ in range(20):
        pyautogui.scroll(500)
        time.sleep(0.1)

    # Click video player
    print(" Clicking on video player at (591, 686)...")
    pyautogui.moveTo(591, 686)
    pyautogui.click()
    time.sleep(1)

    # Fullscreen - try double click
    print(" Attempting to fullscreen with double-click...")
    pyautogui.moveTo(982, 528)
    pyautogui.doubleClick()
    time.sleep(2)

    # Resume playback if paused
    print(" Checking for visible play button...")
    play_btn = safe_locate_center("ptc_play_button.png", confidence=0.8)
    if play_btn:
        print(f" Found play button at {play_btn}, clicking to resume playback.")
        pyautogui.moveTo(play_btn)
        pyautogui.click()
        time.sleep(1)
    else:
        print(" No play button found — assuming video is playing.")

    

    # Reset scroll again in case any popups appeared
    pyautogui.scroll(9999)
    return url
