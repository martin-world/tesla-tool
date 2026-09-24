# Tesla Video Merger

[English](README_EN.md) | [中文](README.md)

A pure graphical (GUI) automation tool specifically designed for Tesla Dashcam and Sentry Mode videos. **Zero command-line prompt windows**, supports dynamic recording timestamp watermarks, and features a unified standard Python cross-platform build script. **Running the build script once generates native desktop applications for both macOS and Windows directly in the `dist/` folder.**

---

## 🌟 Key Features

1. **One-Click Multi-Platform Packaging (`build.py`)**:
   - Run `python build.py` once to output both native desktop deliverables in `dist/`:
     - **`TeslaVideoMerger.app`** (macOS Native Application Bundle)
     - **`TeslaVideoMerger.exe`** (Windows Standalone GUI Executable)
   - Zero redundant zip archives or extra folders—clean, ready-to-run deliverables.
2. **Strictly One Video Per Perspective**:
   - For every camera angle (`front`, `back`, `left_repeater`, `right_repeater`), all sequential video clips are merged into **strictly one single continuous video**.
   - No scattered subtitle files, no cluttered outputs.
3. **Dynamic Timestamp Watermark (Optional)**:
   - Parses the initial recording timestamp from filenames (e.g., `2026-08-02_05-52-17`).
   - Automatically increments second-by-second during playback, precisely matching the true recording time of each clip.
   - Powered by single-pass hardware acceleration (Apple Silicon `VideoToolbox` on macOS, NVENC/QSV on Windows).
   - Can be toggled on/off in the GUI (off = instant lossless stream copy in 1–2 seconds via `-c copy`).
4. **Pure Native GUI (Zero Black Console Windows)**:
   - Supports **instant English / Chinese bilingual toggle** (language combobox in the top-right corner, auto-detects system locale).
   - Built with Python's native `tkinter/ttk` with platform-native styling.
   - **Auto-scans** video clips as soon as a folder is selected.
   - **Defaults output directly to Desktop**, with a one-click "Output to Desktop" reset button.
   - Multi-threaded background processing ensures the UI stays responsive without freezing.
   - "Open Output Folder" button available immediately upon completion.
5. **Smart Filtering & Chronological Sorting**:
   - Strictly matches Tesla naming convention: `YYYY-MM-DD_HH-MM-SS-<camera>.mp4`.
   - Automatically filters out metadata (`event.json`), low-res thumbnails (`thumb.mp4`), and OS hidden files (`._*`, `.DS_Store`).
   - Sorts all clips in ascending chronological order before merging.

---

## 📁 Project Structure

```text
tesla/
├── main.py                    # Main program entry point (Pure GUI)
├── gui.py                     # Tkinter/ttk desktop GUI implementation
├── merger.py                  # Core video parsing, filtering, and merging engine
├── build.py                   # Universal cross-platform build script (generates .app & .exe)
├── tesla_merger.spec          # PyInstaller packaging specification
├── requirements.txt           # Python dependencies
├── .github/workflows/build.yml# GitHub Actions CI workflow
├── README.md                  # Chinese documentation
└── README_EN.md               # English documentation
```

---

## 🚀 Method 1: Run Directly via Python

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Launch the GUI with standard Python on either macOS or Windows:
```bash
python main.py
```

> **Usage Steps**:
> 1. Click **Browse...** next to **Video Input Directory** and select your Tesla video folder (e.g., from your USB drive). The app will automatically scan and list all detected perspectives.
> 2. The **Merge Output Directory** defaults to your Desktop. Click **Output to Desktop** at any time to reset.
> 3. Optional: Check or uncheck **Burn Dynamic Timestamp Watermark** according to your preference.
> 4. Click **🚀 Start Merge**. Once completed, click **Open Output Directory** to view your merged videos.

---

## 📦 Method 2: Universal One-Click Packaging

Run the universal build command on any machine:

```bash
python build.py
```

The script automatically manages dependencies, clears old build artifacts, and produces pure native applications for both platforms in the `dist/` directory:

```text
dist/
├── TeslaVideoMerger.app       # [macOS] Native Application (Double-click to run, no terminal)
└── TeslaVideoMerger.exe       # [Windows] Native GUI Executable (Double-click to run, no cmd window)
```

> **macOS Security Note**:  
> If macOS displays a gatekeeper warning on first open because the app is unsigned, simply run:
> ```bash
> xattr -cr dist/TeslaVideoMerger.app
> ```
> Or go to **System Settings -> Privacy & Security** and click **Open Anyway**.

---

## 🌐 Method 3: Cloud Automated CI/CD (GitHub Actions)

A pre-configured `.github/workflows/build.yml` workflow is included. When pushed to GitHub, GitHub Actions will automatically run `python build.py` on cloud Windows and macOS virtual runners and provide downloadable artifacts.

---

## ❓ Frequently Asked Questions (FAQ)

**Q1: Why is merging without timestamp watermark so fast?**
- When the timestamp watermark is unchecked, FFmpeg utilizes **stream copy** (`-c copy`). It performs raw packet container muxing without decoding or re-encoding video frames. It finishes in 1–2 seconds at pure disk I/O speed, preserving 100% original quality.

**Q2: Can it handle subfolders like `SavedClips` or `SentryClips`?**
- Yes! The **Recursive Scan Subfolders** option is enabled by default. It traverses all nested event subdirectories and aggregates matching clips by camera perspective chronologically.

**Q3: What are the output filenames?**
- Output files follow the format: `Tesla_{camera}_{start_time}_to_{end_time}.mp4`  
  Example: `Tesla_front_2026-08-02_05-52-17_to_06-30-00.mp4`.
