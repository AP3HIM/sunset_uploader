import time
import pyautogui
import csv
import os

# get schedule from schedule.csv
SCHEDULE_PATH = os.path.join(os.path.dirname(__file__), "schedule.csv")
SKIP_MINUTES = 5  # Skip first and last 5 minutes
CLIP_DURATION = 60  # Seconds

def record_movie(title, runtime_minutes):
    effective_runtime = max(runtime_minutes - 2 * SKIP_MINUTES, 0)
    total_clips = effective_runtime * 60 // CLIP_DURATION

    print(f" Starting recording for {title} — {total_clips} clips")
    time.sleep(3)

    for i in range(total_clips):
        print(f" Clip {i + 1}/{total_clips} of {title}")
        pyautogui.hotkey('win', 'alt', 'r')  # Start
        time.sleep(CLIP_DURATION)
        pyautogui.hotkey('win', 'alt', 'r')  # Stop
        time.sleep(2)  # Pause between clips

    print(f" Finished recording {title}!\n")

def record_all_from_schedule():
    if not os.path.exists(SCHEDULE_PATH):
        print(" schedule.csv not found.")
        return

    with open(SCHEDULE_PATH, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['title']
            try:
                runtime = int(row['runtime'])
                record_movie(title, runtime)
            except Exception as e:
                print(f" Skipping {title} due to error: {e}")

if __name__ == "__main__":
    record_all_from_schedule()
