import os
import csv
import random
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROGRESS_FILE = os.path.join(BASE_DIR, "progress.csv")
SCHEDULE_FILE = os.path.join(BASE_DIR, "schedule.csv")

MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

MOVIE_URLS_FILE = os.path.join(
    BASE_DIR,
    "movie_urls.csv"
)

MAX_CLIPS_PER_RUN = 10

SUNSET_VAR = "uploaded through sunsetuploader.com"

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

def load_movie_urls():
    urls = {}

    with open(
        MOVIE_URLS_FILE,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            urls[row["slug"]] = row["video_url"]

    return urls

def load_progress():
    progress = {}

    if not os.path.exists(PROGRESS_FILE):
        return progress

    with open(PROGRESS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            progress[row["title"]] = int(row["timestamp"])

    return progress


def save_progress(progress):
    with open(PROGRESS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title", "timestamp"]
        )

        writer.writeheader()

        for title, timestamp in progress.items():
            writer.writerow({
                "title": title,
                "timestamp": timestamp
            })

def get_schedule():
    with open(SCHEDULE_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def is_supported_url(url):
    """ffmpeg can stream-extract from our CDN but not archive.org's redirect/auth flow."""
    return "archive.org" not in url

def create_clip(source_url, slug, timestamp):

    output_file = os.path.join(
        MEDIA_DIR,
        f"{slug}_{timestamp}.mp4"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(timestamp),
        "-i",
        source_url,
        "-t",
        "60",

        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",

        output_file
    ]

    print("Creating clip...")
    subprocess.run(cmd, check=True)

    return output_file

def upload_clip(video_file, caption):
    cmd = [
        "python",
        os.path.join(BASE_DIR, "upload.py"),

        "--caption",
        caption,

        "--video",
        video_file,

        "--platforms",
        "tiktok",
        "instagram",
        #"twitter"
    ]

    subprocess.run(cmd, check=True)


def main():
    progress = load_progress()
    schedule = get_schedule()
    movie_urls = load_movie_urls()

    clips_created = 0

    for row in schedule:

        if clips_created >= MAX_CLIPS_PER_RUN:
            break

        slug = row["title"]

        current_timestamp = progress.get(slug, 0)

        print(f"\nProcessing {slug}")
        print(f"Timestamp: {current_timestamp}")

        if slug not in movie_urls:
            print(f"Skipping {slug} (missing movie id)")
            continue

        movie_url = movie_urls[slug]

        if not is_supported_url(movie_url):
            print(f"Skipping {slug} — archive.org URL not supported by ffmpeg pipeline: {movie_url}")
            continue

        clip_file = create_clip(
            movie_url,
            slug,
            current_timestamp
        )

        caption = random.choice(CAPTIONS).format(
            title=slug.replace("-", " ").title()
        )

        upload_clip(
            clip_file,
            caption
        )

        progress[slug] = current_timestamp + 60
        save_progress(progress)

        clips_created += 1

    print("Done.")

if __name__ == "__main__":
    main()