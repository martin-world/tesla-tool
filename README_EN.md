# Tesla Video Merger

[English](README_EN.md) | [中文](README.md)

A pure graphical (GUI) automation tool specifically designed for Tesla Dashcam and Sentry Mode videos. **Zero command-line prompt windows**, supports dynamic recording timestamp watermarks, and strictly guarantees **only one merged long video per camera perspective**.

---

## 🌟 Key Features

- **Strictly One Video Per Perspective**: For every camera angle (`front`, `back`, `left_repeater`, `right_repeater`), all clips are merged into **one single continuous video**, with zero redundant `.srt` or temporary clutter.
- **Pure Native GUI (Zero Black Console Windows)**: Standard system window style with instant English / Chinese bilingual toggle (auto-detects system locale).
- **Dynamic Timestamp Watermark (Optional)**: Automatically increments second-by-second with playback based on recording time; powered by hardware acceleration (Mac VideoToolbox / Win NVENC/QSV); off = instant lossless stream copy (`-c copy`) in 1–2 seconds.
- **Smart Filtering & Chronological Sorting**: Matches standard Tesla filenames, automatically excludes metadata (`event.json`), low-res thumbnails (`thumb.mp4`), and OS hidden files (`._*`).
- **Smart Path Management**: Auto-scans clips upon folder selection; output directory **defaults directly to Desktop**, with a one-click reset button.

---

## 🚀 Part 1: Download & Use via Release (Recommended)

If you just want to use the application without tinkering with Python source code, download the pre-built desktop application directly from GitHub Releases:

### 1. Download for Your Platform

Go to the **[Releases Page](../../releases)** to download the latest executable:

- **macOS Users**: Download **`TeslaVideoMerger.app`**
- **Windows Users**: Download **`TeslaVideoMerger.exe`**

> All Release packages in this project are standalone desktop executables without redundant zip archives. Download and run immediately.

---

### 2. First-Run Notes

- **macOS**:  
  Because the application is built without an expensive Apple Developer certificate, macOS Gatekeeper may show an "unidentified developer" or "damaged app" prompt upon first launch. You can easily remove this security quarantine:
  - **Option A (Quickest)**: Open Terminal and run:
    ```bash
    xattr -cr /path/to/TeslaVideoMerger.app
    # For example, if downloaded to Downloads folder:
    xattr -cr ~/Downloads/TeslaVideoMerger.app
    ```
  - **Option B**: Open macOS **System Settings** -> **Privacy & Security**, scroll down to find the blocked app message, and click **Open Anyway**.
- **Windows**:  
  Double-click **`TeslaVideoMerger.exe`** directly. The app is compiled in pure GUI mode with **no black command prompt / CMD popups**.

---

### 3. Step-by-Step GUI Usage

1. **Select Video Input Directory**:
   - Click **Browse...** next to **Video Input Dir** and select your USB flash drive or folder containing Tesla clips.
   - The app will **automatically scan** and detect all perspectives (front, back, left/right repeaters). The table in the center will display clip counts, time ranges, and the unique target filename for each perspective.
2. **Confirm Output Directory**:
   - The output directory defaults to your **Desktop**.
   - If changed, click **To Desktop** at any time to restore the default path.
3. **Choose Timestamp Watermark Option**:
   - **Checked (Burn dynamic timestamp watermark)**: Burns the true recording timestamp (`YYYY-MM-DD HH:MM:SS`) into the bottom-left corner with hardware acceleration, incrementing smoothly with playback.
   - **Unchecked**: Uses lossless stream copy (`-c copy`), completing dozens of clips in 1–2 seconds with 100% original video quality.
4. **Start Merge**:
   - Click **🚀 Start Merge**. The background thread handles processing smoothly without freezing the UI.
   - Once finished, click **📂 Open Output Folder** to reveal your merged video files in Finder or File Explorer.
5. **Language Switch**:
   - Toggle between **English** and **简体中文** anytime via the dropdown in the top-right corner. All labels, buttons, tables, and dialogs update instantly.

---

## 🛠️ Part 2: Build from Source & Self Packaging (Developers)

If you would like to run from source code, make modifications, or compile native packages locally:

### 1. Prerequisites & Dependencies

Ensure Python 3.8+ is installed on your machine:

```bash
# Recommended: create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows

# Install core dependencies (PyInstaller and cross-platform FFmpeg binaries)
pip install -r requirements.txt
```

---

### 2. Method A: Run Directly from Source

Launch the desktop GUI without packaging:

```bash
python main.py
```

---

### 3. Method B: One-Click Local Multi-Platform Build

A universal cross-platform packaging script [`build.py`](build.py) is provided. **Running it once simultaneously generates native desktop deliverables for both macOS and Windows in `dist/`**, without creating zip archives:

```bash
python build.py
```

After building, the clean deliverables will appear in `dist/`:

```text
dist/
├── TeslaVideoMerger.app       # macOS Native Application Bundle
└── TeslaVideoMerger.exe       # Windows Standalone GUI Executable
```

> **Build Mechanism**:  
> - On macOS: Compiles `TeslaVideoMerger.app` with embedded FFmpeg via PyInstaller, and synthesizes the dependency-free Windows `TeslaVideoMerger.exe` via official Windows PE32+ GUI stubs (`distlib/w64.exe`).
> - On Windows: Compiles the native Windows PE executable directly.

---

## 📁 Project Directory Structure

```text
tesla/
├── main.py                    # Main program entry point (Pure GUI)
├── gui.py                     # Tkinter/ttk desktop GUI (with English / Chinese toggle)
├── merger.py                  # Core video parsing, filtering, and merging engine
├── build.py                   # Universal cross-platform build script (.app & .exe in 1 run)
├── tesla_merger.spec          # PyInstaller packaging specification
├── requirements.txt           # Python dependencies
├── .github/workflows/build.yml# GitHub Actions CI workflow
├── README.md                  # Chinese documentation
└── README_EN.md               # English documentation
```
