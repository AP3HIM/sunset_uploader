import pyautogui
import time
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '../images')

def get_latest_video(folder):
    video_files = sorted(glob.glob(os.path.join(folder, "*.mp4")), key=os.path.getmtime, reverse=True)
    return video_files[0] if video_files else None

def upload_instagram(caption, video_file):

    print(" Looking for 'Create' button...")
    create_button = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'insta_create_button.png'), confidence=0.8)
    if create_button:
        pyautogui.click(create_button)
        print(" Clicked 'Create' button")
        time.sleep(2)
    else:
        print(" Could not find 'Create' button")
        return  
    
    print(" Looking for first 'Post' button...")
    new_ig_post_btn = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'new_ig_post_btn.png'), confidence=0.8)
    if new_ig_post_btn:
        pyautogui.click(new_ig_post_btn)
        print(" Clicked first 'Post' button")
        time.sleep(2)
    else:
        print(" Could not find first 'Post' button")
        return  

    print(" Looking for 'Select file' button...")
    select_button = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'insta_select_file.png'), confidence=0.8)
    if select_button:
        pyautogui.click(select_button)
        print(" Clicked 'Select from computer'")
    else:
        print(" Could not find 'Select file' button")
        return

    time.sleep(2)
    print(" Typing video path...")
    pyautogui.write(video_file)
    pyautogui.press('enter')
    time.sleep(5)

    for step in range(2):
        print(" Clicking 'Next' button...")
        for attempt in range(3):
            next_button = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'insta_next_file.png'), confidence=0.7)
            if next_button:
                pyautogui.click(next_button)
                print(f" Clicked 'Next' (step {step + 1}, attempt {attempt + 1})")
                time.sleep(2)
                break
            else:
                print(f" Retrying 'Next' (step {step + 1}, attempt {attempt + 1})")
                time.sleep(2)
        else:
            print(" Could not find 'Next' button after 3 tries")
            return

    time.sleep(2)

    print(" Looking for caption box...")
    caption_box =  pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'insta_caption_new.png'), confidence=0.7)
    if caption_box:
        pyautogui.click(caption_box)
        time.sleep(0.5)
        pyautogui.write(caption, interval=0.05)
    else:
        print(" Could not find caption box.")
        return

    print(" Scrolling to find 'Share' button...")
    pyautogui.scroll(-800)
    time.sleep(1)

    print(" Looking for 'Share' button...")
    share_button = pyautogui.locateCenterOnScreen(os.path.join(IMAGES_DIR, 'insta_share_file.png'), confidence=0.8)
    if share_button:
        pyautogui.click(share_button)
        print(" Posted to Instagram!")
    else:
        print(" Could not find 'Share' button.")

if __name__ == "__main__":
    video_file = get_latest_video(os.path.join(os.getcwd(), "media"))
    if not video_file:
        print(" No video found.")
    else:
        caption = "Watch full movies for free at papertigercinema.com. #Cinema #ClassicMovies #Indie"
        upload_instagram(caption, video_file)
