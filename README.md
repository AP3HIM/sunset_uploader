# Paper Tiger Cinema Auto Uploader Bot

## What It Does

This automation bot visits a website, records a 60-second (or longer) clip, converts the video to vertical 9:16 format if needed, and uploads it to TikTok, Instagram, and X (formerly Twitter). 

A YouTube upload script is included (`upload_youtube.py`), but we recommend caution with YouTube since it may be stricter and could result in account penalties. If you only want to cross-post existing videos without recording, you can run any of the individual upload scripts directly.

## How It Works

The core script is `main.py`, which orchestrates the entire process:

1. Sets a list of randomized captions to avoid detection and add variety.
2. Reads from `schedule.csv` to determine which movies to process.
3. Checks `progress.csv` for where it left off in each movie.
4. Launches Chrome and navigates to the movie URL with the correct timestamp.
5. Records a 60-second clip using the Windows Game Bar (Alt+Win+R).
6. Moves the raw recording to the `media/` folder.
7. Converts the clip to 9:16 format using `ffmpeg`.
8. Uploads the final video to TikTok, Instagram, and Twitter with a random caption.
9. Updates `progress.csv` with the new timestamp.
10. Marks the movie as complete in `completed.txt` if the runtime is finished.

You can control how many clips run in one session by setting `MAX_CLIPS_PER_RUN` in `main.py`. We recommend 10–15 clips per day, though higher volumes usually work as well.

## Features

- Desktop GUI with start, stop, pause, and resume controls (built with Tkinter)
- Automatically launches and controls Chrome
- Supports both Video.js and fallback React Player video formats
- Captions are randomized for each post
- Includes fallback logic and error handling

## Folder Structure

- `main.py` – Main script that runs the bot
- `amp/` – Contains:
  - `upload_tiktok.py`
  - `upload_instagram.py`
  - `upload_twitter.py`
  - `upload_youtube.py`
- `build/`, `dist/`, `gui.exe` – GUI build assets (if compiled with PyInstaller)
- `converted/` – Stores final 9:16 converted clips
- `media/` – Stores raw screen recordings before conversion
- `images/` – Button images used for automation (e.g., upload buttons)
- `convert_clip.py` – Converts clips to vertical 9:16 format using `ffmpeg`
- `find_location.py` – Tool to help identify on-screen coordinates
- `gui.py` – GUI interface with start/stop/pause/play functionality
- `record_clip.py` – Records screen clips using Game Bar
- `completed.txt` – Logs finished movies to prevent reprocessing
- `progress.csv` – Stores current timestamp for each movie
- `schedule.csv` – Movie titles and runtimes for the bot to process

## Demo Video

Watch a full walkthrough of the tool in action:  
[Watch the demo](https://youtu.be/yh1kear4q-E)

## How to Run It

1. Install Python 3.x
2. Run `pip install -r requirements.txt`
3. Sign in to your social media accounts (TikTok, Instagram, Twitter) on Chrome
4. Run `main.py` or use `gui.py` for a desktop interface
5. To create a standalone app, compile the GUI with PyInstaller

## Developer Notes

This tool uses the Windows Game Bar (`Win + Alt + R`) to record video. On some machines, the Game Bar may take a few seconds to open or behave inconsistently. You may need to give it a moment before it starts recording reliably.

## Privacy & Account Info

This tool does not collect, store, or transmit any personal data. You must already be signed into your accounts when using this bot. Its only purpose is to automate content creation and publishing to help creators streamline their workflow.
