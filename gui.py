import tkinter as tk
from tkinter import scrolledtext
import threading
import subprocess
import os
import signal
from PIL import Image, ImageTk
import sys 

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

process_ref = {"process": None}

icon_path = os.path.join(BASE_DIR, "images", "logo.ico")


def run_main_py(log_widget):
    def task():
        interpreter = "python"
        process = subprocess.Popen(
            [interpreter, os.path.join(BASE_DIR, 'main.py')],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        process_ref["process"] = process
        for line in process.stdout:
            log_widget.insert(tk.END, line)
            log_widget.see(tk.END)
        process.wait()
        log_widget.insert(tk.END, "\n Main script finished.\n")
    threading.Thread(target=task).start()

def stop_main_py(log_widget):
    process = process_ref.get("process")
    if process and process.poll() is None:
        process.terminate()
        log_widget.insert(tk.END, "\n Uploading stopped.\n")

def pause_main_py(log_widget):
    process = process_ref.get("process")
    if process and process.poll() is None:
        os.kill(process.pid, signal.SIGSTOP)
        log_widget.insert(tk.END, "\n Uploading paused.\n")

def unpause_main_py(log_widget):
    process = process_ref.get("process")
    if process and process.poll() is None:
        os.kill(process.pid, signal.SIGCONT)
        log_widget.insert(tk.END, "\n Uploading resumed.\n")

def show_completed():
    completed_path = os.path.join(BASE_DIR, "completed.txt")
    if not os.path.exists(completed_path):
        return "completed.txt not found."
    with open(completed_path, encoding="utf-8") as f:
        return f.read()

def refresh_completed(completed_box):
    completed_box.delete("1.0", tk.END)
    completed_box.insert(tk.END, show_completed())

def build_gui():
    root = tk.Tk()
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    root.title("Paper Tiger Uploader")
    root.geometry("950x650")
    root.configure(bg="#1a1a1a")

    logo_path = os.path.join(BASE_DIR, "images", "logo.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        img = img.resize((100, 100))
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(root, image=logo_img, bg="#1a1a1a")
        logo_label.image = logo_img
        logo_label.pack(anchor='nw', padx=10, pady=10)

    # Buttons
    btn_frame = tk.Frame(root, bg="#1a1a1a")
    btn_frame.pack(pady=10)

    log_output = scrolledtext.ScrolledText(root, height=15, bg="#262626", fg="white")
    log_output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    start_btn = tk.Button(btn_frame, text=" Start Uploading", font=("Segoe UI", 12, "bold"),
                          bg="#ff9900", fg="black", padx=12, pady=8,
                          command=lambda: run_main_py(log_output))
    start_btn.grid(row=0, column=0, padx=8)

    pause_btn = tk.Button(btn_frame, text=" Pause", font=("Segoe UI", 12),
                          bg="#666", fg="white", padx=12, pady=8,
                          command=lambda: pause_main_py(log_output))
    pause_btn.grid(row=0, column=1, padx=8)

    unpause_btn = tk.Button(btn_frame, text=" Unpause", font=("Segoe UI", 12),
                            bg="#666", fg="white", padx=12, pady=8,
                            command=lambda: unpause_main_py(log_output))
    unpause_btn.grid(row=0, column=2, padx=8)

    stop_btn = tk.Button(btn_frame, text=" Stop", font=("Segoe UI", 12),
                         bg="#cc0000", fg="white", padx=12, pady=8,
                         command=lambda: stop_main_py(log_output))
    stop_btn.grid(row=0, column=3, padx=8)

    completed_label = tk.Label(root, text=" Completed Movies", font=("Segoe UI", 12), bg="#1a1a1a", fg="#ffcc00")
    completed_label.pack()

    completed_box = scrolledtext.ScrolledText(root, height=10, bg="#333", fg="white")
    completed_box.pack(padx=10, pady=5, fill=tk.BOTH)
    refresh_completed(completed_box)

    refresh_btn = tk.Button(root, text=" Refresh Completed", command=lambda: refresh_completed(completed_box),
                            bg="#444", fg="white", padx=10)
    refresh_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    build_gui()
