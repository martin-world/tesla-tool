# 特斯拉行车记录仪/哨兵视频合并工具 (Tesla Video Merger)

[中文](README.md) | [English](README_EN.md)

专为特斯拉（Tesla）行车记录仪和哨兵模式视频设计的纯图形化（GUI）自动化合并工具。**无任何命令行黑框**，支持动态时间水印嵌入，严格保证**每个视角合并后只输出唯一的一个完整长视频**。

---

## 🌟 核心特性

- **严格单视角单长视频**：每个视角（`front`、`back`、`left_repeater`、`right_repeater`）合并后仅输出一个完整 MP4 视频，绝无多余 `.srt` 或杂乱临时文件。
- **纯原生 GUI（零黑框终端）**：内置系统风格界面，支持中英文即时无缝切换（自动识别系统语言）。
- **动态时间水印嵌入（可选）**：解析文件名起始时间，随播放逐秒精确递增；启用硬件加速（Mac VideoToolbox / Win NVENC/QSV）；关闭时享受秒级纯无损流拷贝（`-c copy`）。
- **智能过滤与排序**：严格匹配特斯拉规范命名，自动剔除 `event.json`、`thumb.mp4` 及系统隐藏文件（`._*`），按录制时刻精确正序排列。
- **智能路径管理**：自动扫描切片与视角，输出目录**默认设为系统桌面**，并提供一键重置按钮。

---

## 🚀 第一部分：Release 直接下载使用（推荐）

如果您不需要修改源码，可以直接从 GitHub Releases 下载编译好的成品应用程序，开箱即用：

### 1. 下载对应系统的程序

前往仓库的 **[Releases 页面](../../releases)** 下载最新版本的可执行程序：

- **macOS 用户**：下载 **`TeslaVideoMerger.app`**
- **Windows 用户**：下载 **`TeslaVideoMerger.exe`**

> 本项目所有 Release 产物均为独立原生桌面程序，无任何多余的 zip 压缩包，下载即可运行。

---

### 2. 首次启动说明

- **macOS 系统**：
  由于程序未购买昂贵的苹果开发者签名证书，首次打开时系统可能会提示“无法打开”或“安全性拦截”。请通过以下两种方式之一快速解除：
  - **方式 A（最简单）**：打开终端，运行命令清除安全隔离属性：
    ```bash
    xattr -cr /path/to/TeslaVideoMerger.app
    # 例如下载到了下载目录：
    xattr -cr ~/Downloads/TeslaVideoMerger.app
    ```
  - **方式 B**：前往 macOS【系统设置】 -> 【隐私与安全性】，向下滚动找到关于该软件的拦截提示，点击【仍要打开】即可。
- **Windows 系统**：
  直接双击 **`TeslaVideoMerger.exe`** 即可启动。程序采用标准无控制台 GUI 打包，**完全没有黑色 CMD 弹窗**。

---

### 3. 图形界面使用步骤

1. **选择视频输入目录**：
   - 点击【视频输入目录】右侧的【浏览...】，选择行车记录仪 U 盘或存放特斯拉视频的文件夹；
   - 程序将**全自动扫描**并识别所有视角（前视、后视、左右中继），中间表格将实时列出各个视角的片段数、时间跨度及即将输出的唯一文件名。
2. **确认合并输出目录**：
   - 程序启动时默认将输出路径设为您当前系统的**桌面**；
   - 如被修改，随时点击【输出到桌面】即可一键恢复。
3. **选择是否嵌入时间水印**：
   - **勾选【嵌入动态时间水印】**：将真实录制时刻（年-月-日 时:分:秒）高清烧录在视频左下角，播放时随时间递增，并通过显卡硬件加速极速编码；
   - **不勾选水印**：采用纯流拷贝（Stream Copy），100% 原始画质无损合并，数十个切片在 1~2 秒内极速完成。
4. **开始合并**：
   - 点击【🚀 开始合并】，后台线程平稳渲染，主界面丝滑不假死；
   - 合并完成后会弹出提示，点击【📂 打开输出目录】即可直接在访达 (Finder) 或文件资源管理器中查看合并好的完整长视频。
5. **中英文随时切换**：
   - 窗口右上角提供【🌐 语言 / Language】下拉框，支持在简体中文与英文之间即时切换。

---

## 🛠️ 第二部分：自己打包与源码运行（开发者）

如果您希望从源码启动、进行二次开发，或自行在本地构建分发程序，请按以下步骤操作：

### 1. 环境准备与依赖安装

确保本地已安装 Python 3.8 或更高版本，并在项目根目录下安装必要依赖：

```bash
# 建议创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows

# 安装核心依赖 (PyInstaller 与跨平台 FFmpeg 二进制库)
pip install -r requirements.txt
```

---

### 2. 方式 A：源码直接运行

无需打包，直接启动原生图形界面：

```bash
python main.py
```

---

### 3. 方式 B：本地一键生成全平台打包程序

项目内置了跨平台通用打包脚本 [`build.py`](build.py)。**仅需执行一次命令，即可在 `dist/` 目录中同时产出 macOS 与 Windows 两个系统的原生独立应用程序**，不生成任何杂乱压缩包：

```bash
python build.py
```

执行完毕后，`dist/` 目录将直接呈现纯净的成品：

```text
dist/
├── TeslaVideoMerger.app       # macOS 原生独立 App
└── TeslaVideoMerger.exe       # Windows 原生无控制台独立程序
```

> **构建原理说明**：  
> - 在 macOS 环境下：通过 PyInstaller 自动加载 `imageio_ffmpeg` 的动态库生成 `.app`，同时利用 Python 官方 Windows PE32+ GUI 引导器（`distlib/w64.exe`）一并合成出免依赖的 Windows `.exe`。
> - 在 Windows 环境下：直接编译生成 Windows 原生 PE 可执行文件。

---

## 📁 项目目录结构说明

```text
tesla/
├── main.py                    # 程序主入口（纯 GUI 桌面应用）
├── gui.py                     # Tkinter/ttk 桌面交互界面（含中英文双语即时切换）
├── merger.py                  # 核心视频扫描、正则过滤、无损拼接与时间水印渲染引擎
├── build.py                   # 跨平台一键通用打包脚本（单次运行产出 .app 与 .exe）
├── tesla_merger.spec          # PyInstaller 编译配置文件
├── requirements.txt           # Python 依赖清单
├── .github/workflows/build.yml# GitHub Actions 自动化云端构建流水线
├── README.md                  # 中文使用与开发说明文档
└── README_EN.md               # 英文说明文档 (English documentation)
```
