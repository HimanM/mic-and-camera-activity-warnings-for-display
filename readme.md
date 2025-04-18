# 🎮 Busy Status Display System 🧘‍♂️

Ever wish your family could _magically know_ when you're in a meeting, on a call, or deep into a game without interrupting you? This project makes that dream real — by showing a **custom video status** on a second monitor based on your PC’s camera and microphone activity!

## 💡 What It Does

- Detects when your **microphone or camera is in use** (like during meetings or games).
- Plays a **"busy" video** on the screen you choose.
- Switches to an **"available" video** when you’re done.
- Optional full-screen mode if you're AFK (no mouse movement).
- Customizable UI to set:
  - Which monitor to display on
  - Video dimensions
  - Custom video files for "busy" and "free" states

## 🔧 How It Works

1. Reads Windows registry and running processes to determine if any apps are actively using the **microphone or webcam**.
2. Uses **OpenCV** to play videos.
3. A **Tkinter GUI** lets you choose monitor, resolution, and upload your own video files.
4. If you're not moving the mouse for a while in maximized mode, it switches to full screen.

## 🛠️ Requirements

- Python 3.9+
- Windows 10/11
- Non-rooted (admin access not required)
- Dual monitor setup (optional but ideal for the effect)

### Python Packages

Install dependencies:

```bash
pip install opencv-python screeninfo psutil pywin32
```

You might also need `pypiwin32` for some systems:

```bash
pip install pypiwin32
```

## 🚀 How To Use

1. Clone or download the repo.
2. Place your default videos in the `/default` folder:
   - `true_state.mp4` — when you're busy
   - `false_state.mp4` — when you're free
3. Run the app:

```bash
python main.py
```

4. Choose your monitor, width/height, and optionally upload different videos.
5. Click **Start** — and let your screen do the talking!

## 📺 Example Use Case

You’re about to join a Zoom meeting or dive into a Valorant match. Your second monitor automatically starts playing a video like:

 “👋 Hey! I’m currently busy. Please don’t disturb unless it’s an emergency.”

When the meeting/game ends? It switches to:

“🌞 I’m available now. Come say hi!”

## 🔐 Privacy & Safety

No data is uploaded or shared. Everything runs **locally**, and no webcam/mic recording is done — it just detects usage.

## 🧪 Future Ideas

- Play sounds or animations
- LED light sync (like Philips Hue)
- Trigger smart home devices
- Use specific app triggers (e.g., Discord or Teams)

## 🧙‍♂️ Author

Built with love and a bit of Python magic 💻✨  
Just a nerd who wanted to game in peace 😎

---

> _"It's not AFK if your screen says you're busy."_ — Probably Confucius

```


