import pyautogui
import time
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '../images')

def get_latest_video(folder):
    video_files = sorted(glob.glob(os.path.join(folder, "*.mp4")), key=os.path.getmtime, reverse=True)
    return video_files[0] if video_files else None

def upload_twitter(caption, video_file):
    print(" Looking for caption box...")
    caption_box = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'twitter_caption_box.png'), confidence=0.7)
    if caption_box:
        pyautogui.click(caption_box)
        time.sleep(0.5)
        pyautogui.write(caption, interval=0.05)
        print(" Typed caption")
    else:
        print(" Could not find caption box.")
        return

    print(" Looking for media upload button...")
    media_button = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'twitter_media_button.png'), confidence=0.7)
    if media_button:
        pyautogui.click(media_button)
        print(" Clicked media upload button")
        time.sleep(2)

        #  Fix: Clear the filename box and type full path directly
        pyautogui.write(video_file, interval=0.03)
        time.sleep(0.3)
        pyautogui.press('enter')
        print(f" Selected file: {video_file}")
    else:
        print(" Could not find media upload button.")
        return

    print(" Waiting for video to process...")
    time.sleep(20)

    print(" Looking for 'Post' button...")
    post_button = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'twitter_post_button_new.png'), confidence=0.7)
    if post_button:
        pyautogui.click(post_button)
        print("  Tweeted!")
    else:
        print("  Could not find 'Post' button.")


if __name__ == "__main__":
    video_file = get_latest_video(os.path.join(os.getcwd(), "media"))
    if not video_file:
        print(" No video found.")
    else:
        caption = " Watch full movies at papertigercinema.com – free streaming, no login! #MovieNight #ClassicCinema"
        upload_twitter(caption, video_file)
