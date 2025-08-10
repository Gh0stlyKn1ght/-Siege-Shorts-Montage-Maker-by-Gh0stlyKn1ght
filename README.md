# -Siege-Shorts-Montage-Maker-by-Gh0stlyKn1ght
 Siege Shorts Montage Maker - Drag and Drop options

````markdown
# 🎯 Siege Shorts Montage Maker

A Python + FFmpeg tool to quickly turn *Rainbow Six: Siege* gameplay clips into **YouTube Shorts** with:
- **Auto cropping to 9:16** (crosshair centered)
- **Speed-up effect** (e.g., 5x faster)
- **Custom background music** at any starting time
- **NVENC GPU acceleration** for fast encoding
- Optimized YouTube export settings

---

## 📌 Features
- Batch process **multiple clips** in one go
- Keep your crosshair perfectly centered in the frame
- Add copyright-free background music
- Start music at any time offset (e.g., 10 seconds in)
- Export using YouTube’s recommended encoding
- Hardware-accelerated encoding for speed

---

## 📜 Requirements
- **Python 3.9+** (Tested on 3.13)
- **FFmpeg** installed and added to system PATH  
  [FFmpeg Download](https://ffmpeg.org/download.html)
- Python packages:
  ```bash
  pip install moviepy
````

---

## ⚡ Basic Usage

To process a **single video**:

```bash
python siege_montage_maker.py -i "clip1.mp4" -o "clip1_shorts.mp4" --music "PYTI - I Wanna Dance [NCS Release].mp3" --music-start 10 --nvenc --h264 --yt --shorts --speed 5 --shortest
```

**Arguments:**

| Option          | Description                                  |
| --------------- | -------------------------------------------- |
| `-i`            | Input video file                             |
| `-o`            | Output video file                            |
| `--music`       | MP3 file for background music                |
| `--music-start` | Second in the video where the music starts   |
| `--speed`       | Speed multiplier for the video               |
| `--shorts`      | Converts to vertical 9:16 aspect ratio       |
| `--nvenc`       | Uses NVIDIA GPU acceleration                 |
| `--yt`          | Applies YouTube export settings              |
| `--shortest`    | Ends the video when the shortest stream ends |

---

## 🗂 Batch Processing with `.bat` File

### 1️⃣ Place the `.bat` File

Put `process_clips.bat` in the same folder as:

* Your `siege_montage_maker.py` script
* Your `.mp4` clips
* Your `.mp3` music file

---

### 2️⃣ Example `process_clips.bat`

```batch
@echo off
REM ======= SETTINGS =======
set MUSIC="PYTI - I Wanna Dance [NCS Release].mp3"  REM Change this to your music file
set SPEED=5                                         REM Speed multiplier for the video
set MUSIC_START=10                                  REM Start music at this second
REM ========================

set COUNT=0
for %%f in (*.mp4) do (
    set /a COUNT+=1
)
set INDEX=0

for %%f in (*.mp4) do (
    set /a INDEX+=1
    echo Processing %%INDEX%% of %COUNT%%: %%f
    python siege_montage_maker.py -i "%%f" -o "%%~nf_shorts.mp4" ^
      --music %MUSIC% ^
      --music-start %MUSIC_START% ^
      --nvenc --h264 --yt --shorts --speed %SPEED% --shortest
)
pause
```

---

### 3️⃣ Changing Settings

| Setting       | Description                                            |
| ------------- | ------------------------------------------------------ |
| `MUSIC`       | The MP3 file to use for the background music           |
| `SPEED`       | Speed multiplier for the video (e.g., `5` = 5x faster) |
| `MUSIC_START` | The time (in seconds) when music starts playing        |

---

### 4️⃣ Running the Batch File

1. Place `.bat` file, `.mp4` clips, `.mp3` file, and Python script together in the same folder.
2. Double-click the `.bat` file.
3. It will process **all `.mp4` files** in the folder automatically.
4. Outputs will be saved as `originalfilename_shorts.mp4`.

💡 **Tip:** To process only certain videos, put those `.mp4` files into a separate folder with the `.bat` file before running.

---

## 📄 License

This project is licensed under the **MIT License** — you are free to use, modify, and share it, but must include the copyright notice.

```
MIT License

Copyright (c) 2025  "Mr. Gh0stly"

Permission is hereby granted, free of charge, to any person obtaining a copy...
[full MIT text here]
```

---

## 👤 Credits

**Developed by:** "Mr. Gh0stly"
**GitHub:** [Gh0stlyKn1ght](https://github.com/Gh0stlyKn1ght)
**Music Example:** *PYTI - I Wanna Dance \[NCS Release]* (Copyright Free via NCS)

---

## 📹 Example Workflow

1. Record Rainbow Six Siege gameplay
2. Drop the `.mp4` into the working folder
3. Run the `.bat` file
4. Upload the resulting `_shorts.mp4` file directly to YouTube Shorts

---
