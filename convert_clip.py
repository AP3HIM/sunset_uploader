import os
import subprocess
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def convert_latest_clip():
    input_dir = os.path.join(BASE_DIR, 'media')
    output_dir = os.path.join(BASE_DIR, 'converted')
    os.makedirs(output_dir, exist_ok=True)

    mp4_files = sorted(glob.glob(os.path.join(input_dir, '*.mp4')), key=os.path.getmtime, reverse=True)
    if not mp4_files:
        print(" No MP4 files found to convert.")
        return

    input_path = mp4_files[0]
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_converted.mp4")  

    print(f" Converting '{input_path}' to 9:16 vertical format...")
    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-c:a', 'copy',
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f" Conversion complete: {output_path}")
    except subprocess.CalledProcessError as e:
        print(" Conversion failed:", e)

if __name__ == '__main__':
    convert_latest_clip()
