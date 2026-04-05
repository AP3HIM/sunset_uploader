import pyautogui 
import time
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '../images')

def get_latest_video(folder):
    video_files = sorted(glob.glob(os.path.join(folder, "*.mp4")), key=os.path.getmtime, reverse=True)
    return video_files[0] if video_files else None

def safe_locate_center(image_name, confidence=0.7):
    try:
        return pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, image_name), confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return None

def click_image(image_name, confidence=0.7, max_retries=5, wait=1):
    for attempt in range(max_retries):
        print(f" Searching for '{image_name}' (attempt {attempt + 1})")
        location = safe_locate_center(image_name, confidence)
        if location:
            pyautogui.click(location)
            print(f" Clicked '{image_name}'")
            time.sleep(wait)
            return True
        time.sleep(wait)
    print(f"  Failed to find '{image_name}' after {max_retries} attempts")
    return False

def set_youtube_title(caption):
    print(" Setting YouTube video title...")

    for attempt in range(5):
        try:
            title_box = pyautogui.locateCenterOnScreen(
                os.path.join(IMAGES_DIR, 'yt_title_new.png'),
                confidence=0.65
            )
            if title_box:
                pyautogui.click(title_box)
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(caption, interval=0.05)
                print("  Wrote title via image recognition")
                return
            else:
                print(f" Attempt {attempt + 1}/5: Image not found.")
                time.sleep(0.5)
        except pyautogui.ImageNotFoundException:
            print(f" Attempt {attempt + 1}/5: Image lookup failed.")
            time.sleep(0.5)

    # Fallback coordinates near center of title box: (742, 507)
    print(" Image detection failed — trying fallback coordinates.")
    fallback_coords = [
        (742, 507), (738, 505), (745, 509), (747, 503),
        (735, 508), (740, 510), (750, 507), (741, 502), (739, 506)
    ]

    for x, y in fallback_coords:
        try:
            pyautogui.click(x, y)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(caption, interval=0.05)
            print(f"  Wrote title via fallback at ({x}, {y})")
            return
        except Exception as e:
            print(f"  Failed to write title at ({x}, {y}): {e}")
            continue

    print("  Failed to set YouTube title using both image and fallback methods.")

def upload_youtube(caption, video_file):
    print("  Starting YouTube Shorts upload...")

    if not click_image('yt_create_button.png', confidence=0.7):
        return
    if not click_image('yt_upload_video.png', confidence=0.7):
        return
    if not click_image('yt_select_files.png', confidence=0.7):
        return

    print(" Typing file path...")
    pyautogui.write(video_file)
    time.sleep(1)
    pyautogui.press('enter')

    print(" Waiting for YouTube to load video interface...")
    time.sleep(7)

    set_youtube_title(caption)

    print(" Scrolling to find 'Not made for kids' button...")
    for _ in range(5):
        pyautogui.scroll(-500)
        time.sleep(0.5)

    if not click_image('yt_kids_button.png', confidence=0.7):
        return
    time.sleep(2)

    print(" Clicking 'Next' 3 times...")
    for _ in range(3):
        if not click_image('yt_next_button.png', confidence=0.7):
            return
        time.sleep(1)

    print(" Setting video to Public...")
    if not click_image('yt_public_button.png', confidence=0.7):
        return
    time.sleep(1)

    print(" Publishing video...")
    if not click_image('yt_publish_button.png', confidence=0.7):
        return

    print("  YouTube Shorts upload complete!")

if __name__ == "__main__":
    media_dir = os.path.abspath(os.path.join(BASE_DIR, '../media'))
    video_file = get_latest_video(media_dir)
    if not video_file:
        print("  No video file found.")
    else:
        caption = "Watch for free on papertigercinema.com. Stream classics and hidden gems now!"
        upload_youtube(caption, video_file)
