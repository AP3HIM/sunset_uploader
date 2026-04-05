# upload.py
import os
import time
import argparse
import platform
import subprocess
import pyautogui
import pyautogui as pag
import sys

try:
    import pyperclip
except ImportError:
    pyperclip = None

from amp import upload_instagram_electron, upload_tiktok_electron, upload_twitter_electron
from utils import launch_chrome, open_new_tab_and_search

print("Raw sys.argv:", sys.argv)


def copy_to_clipboard(text):
    if pyperclip:
        pyperclip.copy(text)
        return True
    plat = platform.system()
    try:
        if plat == "Windows":
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            p.stdin.write(text.encode('utf-8'))
            p.stdin.close()
        elif plat == "Darwin":
            p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            p.stdin.write(text.encode('utf-8'))
            p.stdin.close()
        else:
            p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            p.stdin.write(text.encode('utf-8'))
            p.stdin.close()
        return True
    except Exception:
        return False


def paste_path_and_confirm(abs_path):
    try:
        old_clip = pyperclip.paste() if pyperclip else None
    except:
        old_clip = None

    print(f"[DEBUG] Pasting file path: {abs_path}")
    ok = copy_to_clipboard(abs_path)
    time.sleep(0.25)
    if not ok:
        print("[DEBUG] Clipboard copy failed, typing manually")
        pyautogui.write(abs_path, interval=0.02)
    else:
        if platform.system() == 'Darwin':
            pyautogui.hotkey('command', 'v')
        else:
            pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.25)
    pyautogui.press('enter')
    print("[DEBUG] Pressed ENTER after pasting")

    if pyperclip and old_clip is not None:
        time.sleep(0.1)
        pyperclip.copy(old_clip)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--caption',    type=str, default="")
    parser.add_argument('--video',      type=str, required=True)
    parser.add_argument('--platforms',  nargs='+', action='append', default=[])
    parser.add_argument('--mode',       type=str, default="full",
                        choices=["full", "file-select-only", "pag-fallback"])
    # Passed from UploadButton when mode=pag-fallback
    # "1" = DOM handled it, "0" = PAG needs to handle it
    parser.add_argument('--dom-caption', type=str, default="0")
    parser.add_argument('--dom-post',    type=str, default="0")

    args = parser.parse_args()

    caption         = args.caption
    video           = os.path.abspath(args.video)
    platforms       = [p for group in args.platforms for p in group]
    mode            = args.mode
    dom_caption_ok  = args.dom_caption == "1"
    dom_post_ok     = args.dom_post    == "1"

    print(f"DEBUG: caption={caption!r}, video={video!r}, platforms={platforms!r}, mode={mode!r}")
    print(f"File exists? {os.path.exists(video)}")

    # ── Mode: file-select-only ────────────────────────────────────────────────
    # Electron opened the BrowserWindow. PAG just selects the file and exits.
    if mode == "file-select-only":
        platform_arg = platforms[0] if platforms else None
        print(f"File-select-only mode for: {platform_arg}")
        if platform_arg == "tiktok":
            upload_tiktok_electron.select_file_only(video, paste_path_and_confirm)
        elif platform_arg == "instagram":
            upload_instagram_electron.select_file_only(video, paste_path_and_confirm)
        elif platform_arg == "twitter":
            upload_twitter_electron.select_file_only(video, paste_path_and_confirm)
        print("File selection complete. Exiting PAG.")
        return

    # ── Mode: pag-fallback ────────────────────────────────────────────────────
    # DOM already handled some steps. PAG only runs the ones DOM missed.
    if mode == "pag-fallback":
        platform_arg = platforms[0] if platforms else None
        print(f"PAG fallback mode for: {platform_arg}")
        print(f"  DOM caption ok: {dom_caption_ok}")
        print(f"  DOM post ok:    {dom_post_ok}")

        if platform_arg == "tiktok":
            if not dom_caption_ok:
                print("PAG: Handling caption fallback...")
                upload_tiktok_electron.write_caption_pag(caption)
            else:
                print("PAG: Caption already done by DOM, skipping.")

            if not dom_post_ok:
                print("PAG: Handling post button fallback...")
                pag.scroll(-10000)
                time.sleep(0.5)
                upload_tiktok_electron.wait_for_post_button()
            else:
                print("PAG: Post already done by DOM, skipping.")

        print("PAG fallback complete.")
        return

    # ── Mode: full (legacy) ───────────────────────────────────────────────────
    # Opens Chrome externally and does everything via PAG.
    print(f"Full PAG mode for: {platforms}")
    launch_chrome()
    time.sleep(1)

    if 'tiktok' in platforms:
        try:
            open_new_tab_and_search("tiktok.com/upload", delay=1.5)
            upload_tiktok_electron.upload(
                caption, video, paste_path_and_confirm,
                dom_success_caption=False,
                dom_success_post=False,
            )
        except Exception as e:
            print(f"Error during TikTok upload: {e}")

    if 'instagram' in platforms:
        try:
            open_new_tab_and_search("instagram.com/", delay=1.5)
            upload_instagram_electron.upload_instagram(caption, video, paste_path_and_confirm)
        except Exception as e:
            print(f"Error during Instagram upload: {e}")

    if 'twitter' in platforms:
        try:
            open_new_tab_and_search("twitter.com/compose/tweet", delay=1.5)
            upload_twitter_electron.upload_twitter(caption, video, paste_path_and_confirm)
        except Exception as e:
            print(f"Error during Twitter upload: {e}")

    print("Upload process complete!")


if __name__ == "__main__":
    main()