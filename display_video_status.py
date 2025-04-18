import cv2
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk
from screeninfo import get_monitors
import win32api
from ctypes import windll, Structure, c_uint, byref
from tkinter import messagebox
import os
from detect_mic_cam_usage import check_camera_and_mic_status


DEFAULT_TRUE_VIDEO = os.path.abspath("default/busy_state.mp4")
DEFAULT_FALSE_VIDEO = os.path.abspath("default/idle_state.mp4")

class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ("length", c_uint),
        ("flags", c_uint),
        ("showCmd", c_uint),
        ("ptMinPosition_x", c_uint),
        ("ptMinPosition_y", c_uint),
        ("ptMaxPosition_x", c_uint),
        ("ptMaxPosition_y", c_uint),
        ("rcNormalPosition_left", c_uint),
        ("rcNormalPosition_top", c_uint),
        ("rcNormalPosition_right", c_uint),
        ("rcNormalPosition_bottom", c_uint)
    ]

class VideoMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Monitor Trigger")

        self.monitors = get_monitors()
        self.selected_monitor = tk.StringVar()
        self.video_true_path = tk.StringVar(value=DEFAULT_TRUE_VIDEO)
        self.video_false_path = tk.StringVar(value=DEFAULT_FALSE_VIDEO)
        self.video_width = tk.StringVar(value="640")
        self.video_height = tk.StringVar(value="480")
        self.running = True
        self.last_mouse_pos = win32api.GetCursorPos()
        self.last_mouse_time = time.time()

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        row = 0
        ttk.Label(self.root, text="Select Monitor:").grid(row=row, column=0, sticky="w")
        monitor_names = [f"{i+1}: {m.width}x{m.height} ({m.x},{m.y})" for i, m in enumerate(self.monitors)]
        ttk.Combobox(self.root, textvariable=self.selected_monitor, values=monitor_names, width=40).grid(row=row, column=1)

        row += 1
        ttk.Label(self.root, text="Video (Busy state):").grid(row=row, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.video_true_path, width=40).grid(row=row, column=1)
        ttk.Button(self.root, text="Browse", command=lambda: self.browse_file(self.video_true_path)).grid(row=row, column=2)

        row += 1
        ttk.Label(self.root, text="Video (Idle state):").grid(row=row, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.video_false_path, width=40).grid(row=row, column=1)
        ttk.Button(self.root, text="Browse", command=lambda: self.browse_file(self.video_false_path)).grid(row=row, column=2)

        row += 1
        ttk.Label(self.root, text="Video Width:").grid(row=row, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.video_width).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(self.root, text="Video Height:").grid(row=row, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.video_height).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Button(self.root, text="Start", command=self.start_video_thread).grid(row=row, column=1, pady=10)

    def browse_file(self, target_var):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if path:
            target_var.set(path)

    def on_close(self):
        self.running = False
        cv2.destroyAllWindows()
        self.root.destroy()

    def start_video_thread(self):
        if not os.path.exists(self.video_true_path.get()):
            messagebox.showwarning("Missing File", f"True state video not found: {self.video_true_path.get()}")
            return
        if not os.path.exists(self.video_false_path.get()):
            messagebox.showwarning("Missing File", f"False state video not found: {self.video_false_path.get()}")
            return
        # Field validation
        if not self.selected_monitor.get():
            messagebox.showwarning("Missing Monitor", "Please select a monitor.")
            return
        if not self.video_true_path.get():
            messagebox.showwarning("Missing Video", "Please select a video for the BUSY state.")
            return
        if not self.video_false_path.get():
            messagebox.showwarning("Missing Video", "Please select a video for the IDLE state.")
            return
        if not self.video_width.get().isdigit() or not self.video_height.get().isdigit():
            messagebox.showwarning("Invalid Size", "Please enter valid width and height (numbers only).")
            return

        thread = threading.Thread(target=self.play_video_loop, daemon=True)
        thread.start()

    def monitor_mouse(self):
        current_pos = win32api.GetCursorPos()
        if current_pos != self.last_mouse_pos:
            self.last_mouse_pos = current_pos
            self.last_mouse_time = time.time()
        return time.time() - self.last_mouse_time < 5

    def is_maximized(self, hwnd):
        wp = WINDOWPLACEMENT()
        wp.length = 44
        windll.user32.GetWindowPlacement(hwnd, byref(wp))
        return wp.showCmd == 3  # SW_MAXIMIZE

    def play_video_loop(self):
        try:
            mon_index = int(self.selected_monitor.get().split(":")[0]) - 1
            monitor = self.monitors[mon_index]
        except Exception as e:
            print("Invalid monitor selection:", e)
            return

        width = int(self.video_width.get())
        height = int(self.video_height.get())

        prev_flag = None
        full_screen = False

        while self.running:

            is_cam, is_mic = check_camera_and_mic_status()
            current_flag = is_cam or is_mic

            # Only reload video if the status has changed
            if current_flag != prev_flag:
                prev_flag = current_flag
                video_path = self.video_true_path.get() if current_flag else self.video_false_path.get()

                if not video_path:
                    time.sleep(1)
                    continue

                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print(f"Could not open video: {video_path}")
                    time.sleep(1)
                    continue

                cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
                cv2.moveWindow("Video", monitor.x, monitor.y)
                cv2.resizeWindow("Video", width, height)

            if not cap.isOpened():
                time.sleep(1)
                continue

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            cv2.imshow("Video", frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                self.running = False
                break

            hwnd = windll.user32.FindWindowW(None, "Video")
            if hwnd and self.is_maximized(hwnd):
                if not self.monitor_mouse() and not full_screen:
                    cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    full_screen = True
                elif self.monitor_mouse() and full_screen:
                    cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    full_screen = False

        if cap:
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoMonitorApp(root)
    root.mainloop()
