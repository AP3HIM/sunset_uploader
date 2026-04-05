import os
import time
import glob
import pyautogui
import csv
import random
import subprocess
import shutil
import pygetwindow as gw
from pathlib import Path

import amp.upload_instagram as upload_instagram
import amp.upload_tiktok as upload_tiktok
import amp.upload_twitter as upload_twitter

from ptc import automate_ptc_movie, get_movie_title_from_url

# === Paths and constants ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
CONVERTED_DIR = os.path.join(BASE_DIR, 'converted')
SCHEDULE_CSV = os.path.join(BASE_DIR, "schedule.csv")
COMPLETED_FILE = os.path.join(BASE_DIR, "completed.txt")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.csv")

SUNSET_VAR = "uploaded through sunsetuploader.com"

# Captions used for random video uploads
CAPTIONS = [
    f"Start watching {{title}} now on papertigercinema.com!, {SUNSET_VAR}",
    f"Did you know this film is public domain? {{title}}, streaming free on papertigercinema.com!, {SUNSET_VAR}",
    f"You won't believe this scene from {{title}}. Watch on papertigercinema.com, {SUNSET_VAR}",
    f"Classic cinema at its finest: {{title}}, on papertigercinema.com, {SUNSET_VAR}",
    f"Watch {{title}} on papertigercinema.com, free forever, {SUNSET_VAR}",
    f"Now streaming: {{title}}. {SUNSET_VAR}",
    f"Public domain magic: {{title}} is live on papertigercinema.com, {SUNSET_VAR}",
    f"Miss the golden age of film? {{title}} is free to stream right now, {SUNSET_VAR}",
    f"{{title}} is a forgotten gem. Watch the full movie on papertigercinema.com, {SUNSET_VAR}",
    f"Stream {{title}} instantly on papertigercinema.com — no signup required, {SUNSET_VAR}",
    f"Papertigercinema.com brings you {{title}} in all its glory, {SUNSET_VAR}",
    f"This clip from {{title}} is unreal. Full film at papertigercinema.com, {SUNSET_VAR}",
    f"{{title}} deserves a second life. Now streaming for free, {SUNSET_VAR}",
    f"One minute from {{title}}. Watch the rest for free at papertigercinema.com!, {SUNSET_VAR}",
    f"Real cinema: {{title}} is free to stream forever on papertigercinema.com, {SUNSET_VAR}",
    f"{{title}} is 100% free. No cost, just press play, {SUNSET_VAR}",
    f"Find your next favorite film. Try {{title}} on papertigercinema.com, {SUNSET_VAR}",
    f"Hollywood forgot these, but they're fire. {{title}} on papertigercinema.com, {SUNSET_VAR}",
    f"Movies with real soul. Watch {{title}} on papertigercinema.com, {SUNSET_VAR}",
    f"Gotta check out {{title}} on papertigercinema.com, {SUNSET_VAR}",
    f"Tap in to {{title}} on papertigercinema.com, {SUNSET_VAR}",
]


MAX_CLIPS_PER_RUN = 10  # Controls the number of clips generated per run

pyautogui.FAILSAFE = False  # Add this at the top of your script if FAILSAFE is going off

# === Helpers ===
def move_latest_recording():
    source_dir = r"C:\Users\adipa\Videos\Captures"
    os.makedirs(MEDIA_DIR, exist_ok=True)
    mp4s = sorted(glob.glob(os.path.join(source_dir, "*.mp4")), key=os.path.getmtime, reverse=True)
    if not mp4s:
        print(" No recordings found in Captures folder.")
        return
    latest = mp4s[0]
    dest = os.path.join(MEDIA_DIR, os.path.basename(latest))
    try:
        shutil.move(latest, dest)
        print(f" Moved latest recording to media/: {os.path.basename(latest)}")
    except Exception as e:
        print(f" Failed to move video: {e}")

def get_latest_video(folder):
    video_files = sorted(glob.glob(os.path.join(folder, "*.mp4")), key=os.path.getmtime, reverse=True)
    return video_files[0] if video_files else None

# opens chrome
def launch_chrome():
    try:
        os.startfile("chrome")
        print(" Launched Chrome via system call")
        time.sleep(3)
    except Exception as e:
        print(" Chrome launch failed:", e)
        return

    # Wait and find Chrome window
    chrome_window = None
    for _ in range(10):
        windows = gw.getWindowsWithTitle("Chrome")
        if windows:
            chrome_window = windows[0]
            break
        time.sleep(1)

    if not chrome_window:
        print(" Could not detect Chrome window.")
        return

    try:
        chrome_window.activate()
        chrome_window.maximize()
        print(" Activated and maximized Chrome window")
        time.sleep(1)
    except Exception as e:
        print(" Failed to manipulate Chrome window:", e)
    
def open_new_tab_and_search(site_name, delay=6):
    pyautogui.hotkey('ctrl', 't')
    time.sleep(0.5)
    pyautogui.write(site_name)
    pyautogui.press('enter')
    print(f" Opened tab and navigated to {site_name}")
    time.sleep(delay)
    time.sleep(0.5)

def run_record_clip(duration=60):
    print(f" Starting screen recording for {duration} seconds...")
    time.sleep(2)
    pyautogui.hotkey('win', 'alt', 'r')
    time.sleep(2)
    time.sleep(duration)
    pyautogui.hotkey('win', 'alt', 'r')
    print(" Recording stopped.")
# converts to shorts vertical format
def run_convert_clip():
    print(" Converting clip to 9:16 format...")
    result = subprocess.run([
        "python", os.path.join(BASE_DIR, "convert_clip.py")
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(" Conversion error:\n", result.stderr)

def mark_movie_completed(title):
    with open(COMPLETED_FILE, "a", encoding="utf-8") as f:
        f.write(f"{title}\n")

def get_completed_titles():
    if not os.path.exists(COMPLETED_FILE):
        return set()
    with open(COMPLETED_FILE, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def get_schedule():
    with open(SCHEDULE_CSV, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [(row['title'], int(row['runtime'])) for row in reader]

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    progress = {}
    with open(PROGRESS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                progress[row['title']] = int(row['timestamp'])
            except:
                continue
    return progress

def save_progress(progress):
    with open(PROGRESS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'timestamp'])
        writer.writeheader()
        for title, timestamp in progress.items():
            writer.writerow({'title': title, 'timestamp': timestamp})

# === Main Bot Logic ===
def main():
    completed = get_completed_titles()
    schedule = get_schedule()
    progress = load_progress()

    for title, runtime in schedule:
        if title in completed:
            continue

        launch_chrome()
        current_timestamp = progress.get(title, 0)

        print(f" Starting {title} — runtime: {runtime} minutes")
        total_seconds = runtime * 60  

        clip_counter = 0

        while current_timestamp + 60 <= total_seconds:
            if clip_counter >= MAX_CLIPS_PER_RUN:
                print(" Max clips per run reached.")
                save_progress(progress)
                return

            # Re-open the movie tab with the current timestamp
            current_url = f"https://papertigercinema.com/movies/{title}?start={current_timestamp}"
            open_new_tab_and_search(current_url, delay=10)
            print(f" Opened movie page at timestamp={current_timestamp}")

            automate_ptc_movie(current_url, timestamp=current_timestamp)
            run_record_clip(duration=60)

            pyautogui.hotkey('ctrl', 'w')  # Close the movie tab
            time.sleep(2)

            move_latest_recording() # moves recording to the correct folder
            run_convert_clip() # converts the clip; this may take some time

            video_file = get_latest_video(CONVERTED_DIR)
            if not video_file:
                print(" No converted video found.")
                return

            caption = random.choice(CAPTIONS).format(title=title.replace('-', ' ').title())

            open_new_tab_and_search("tiktok.com/upload", delay=10)
            upload_tiktok.upload(caption, video_file)

            open_new_tab_and_search("instagram.com/papertigercinema/", delay=8)
            upload_instagram.upload_instagram(caption, video_file)

            open_new_tab_and_search("twitter.com/compose/tweet", delay=6)
            upload_twitter.upload_twitter(caption, video_file)

            time.sleep(1)

            clip_counter += 1
            current_timestamp += 60
            progress[title] = current_timestamp
            save_progress(progress)


            print(" All featured movies processed!")

if __name__ == "__main__":
    main()
