import pyautogui
import time
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '../images')


def get_latest_video(folder):
    video_files = sorted(
        glob.glob(os.path.join(folder, "*.mp4")),
        key=os.path.getmtime,
        reverse=True
    )
    return video_files[0] if video_files else None


def safe_locate_center(image_path, confidence=0.7):
    try:
        return pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return None


def try_write_caption(caption):
    print(" Looking for caption box...")

    # Try image recognition first
    for attempt in range(5):
        try:
            caption_box = pyautogui.locateCenterOnScreen(
                os.path.join(IMAGES_DIR, 'caption_box.png'),
                confidence=0.65
            )
            if caption_box:
                pyautogui.click(caption_box)
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(caption, interval=0.05)
                print(" Wrote caption via image recognition")
                return
            else:
                print(f" Attempt {attempt + 1}/5: Image not found.")
                time.sleep(0.5)
        except pyautogui.ImageNotFoundException:
            print(f" Attempt {attempt + 1}/5: Image lookup failed.")
            time.sleep(0.5)

    # Fallback coordinates near (881, 641)
    print(" Image detection failed — trying fallback coordinates.")
    fallback_coords = [
        (881, 641), (885, 645), (877, 637), (890, 641),
        (875, 643), (881, 635), (880, 648), (888, 638), (873, 646)
    ]

    for x, y in fallback_coords:
        try:
            pyautogui.click(x, y)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(caption, interval=0.05)
            print(f" Wrote caption via fallback at ({x}, {y})")
            return
        except Exception as e:
            print(f" Failed to write caption at ({x}, {y}): {e}")
            continue

    print("  Failed to set TikTok caption using both image and fallback methods.")


def upload(caption, video_file):
    print(" Looking for 'Select file' button...")
    file_button = safe_locate_center(os.path.join(IMAGES_DIR, 'select_file.png'))
    if file_button:
        pyautogui.click(file_button)
        print(" Found and clicked 'Select file'")
    else:
        print(" Could not find 'Select file' button")
        return

    time.sleep(2)

    print(" Typing file path...")
    pyautogui.write(video_file)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3)

    # Write caption
    try_write_caption(caption)

    print(" Scrolling to find Post button...")
    pyautogui.scroll(-800)
    time.sleep(1)

    print(" Waiting for video to upload fully before looking for 'Post' button...")
    time.sleep(5)

    print(" Looking for 'Post' button...")
    post_button = safe_locate_center(os.path.join(IMAGES_DIR, 'post_file.png'), confidence=0.8)
    if post_button:
        pyautogui.click(post_button)
        print("  Posted successfully!")
    else:
        print("  Could not find 'Post' button")


if __name__ == "__main__":
    video_file = get_latest_video(os.path.join(os.getcwd(), "media"))
    if not video_file:
        print("  No video found.")
    else:
        caption = "Watch for free on papertigercinema.com. Stream classics and hidden gems now!"
        upload(caption, video_file)
