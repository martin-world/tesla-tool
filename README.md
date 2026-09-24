# 特斯拉行车记录仪/哨兵视频合并工具 (Tesla Video Merger)

[中文](README.md) | [English](README_EN.md)

专为特斯拉（Tesla）行车记录仪和哨兵模式视频设计的纯图形化（GUI）自动化合并工具。**无任何命令行黑框**，支持动态时间水印嵌入，通过标准 Python 跨平台构建脚本，**执行一次即可在 `dist/` 目录中直接生成 macOS 与 Windows 的原生安装程序**。

---

## 🌟 核心特性

1. **执行一次，全平台安装产物齐备 (`build.py`)**：
   - 运行一次 `python build.py`，直接在 `dist/` 目录输出：
     - **`TeslaVideoMerger.app`**（macOS 独立桌面应用程序）
     - **`TeslaVideoMerger.exe`**（Windows 独立桌面可执行程序）
   - 不生成任何多余的 zip 压缩包或临时目录，产物干净清晰。
2. **严格单视角单长视频**：
   - 每一个视角（`front`、`back`、`left_repeater`、`right_repeater` 等）合并后，在输出目录中**只输出唯一的一个完整长视频**，绝不产生多余的额外文件。
3. **动态时间水印嵌入（可选，随播放自动递增）**：
   - 自动解析文件名起始时间戳（如 `2026-08-02_05-52-17`），并在视频画面左下角嵌入高清时间水印。
   - **随播放时间逐秒自动累加递增**，即使素材间有时间断层，每个切片也会精准对齐其真实录制时刻。
   - 支持 Mac 硬件加速（VideoToolbox）以及 Windows 硬件加速（NVENC/QSV），单次流水线高效渲染。
   - 界面中可随时勾选开启/关闭水印（关闭时使用秒级纯无损流拷贝 `-c copy`）。
4. **纯原生 GUI（彻底告别黑框命令行）**：
   - 支持**中英文界面即时切换**（右上角语言下拉框，或自动识别系统语言）。
   - 原生系统风格文件夹选择框，选定文件夹后**全自动扫描视角切片**。
   - **默认合并输出到桌面**，点击【输出到桌面】按钮可随时一键重置路径。
   - 界面实时展示检测到的视角、片段数量、时间跨度及目标文件名。
   - 多线程后台渲染，界面丝滑不假死，任务完成后可一键打开输出文件夹。
5. **精准过滤与视角识别**：
   - 严格匹配特斯拉标准切片命名规则：`YYYY-MM-DD_HH-MM-SS-<camera>.mp4`。
   - 自动过滤不符合格式的文件、事件元数据（`event.json`）、低清缩略图（`thumb.mp4`）及系统隐藏文件（`._*`、`.DS_Store`）。

---

## 📁 目录结构

```text
tesla/
├── main.py                    # 主程序入口（纯 GUI 桌面应用）
├── gui.py                     # Tkinter/ttk 现代化图形界面实现
├── merger.py                  # 核心合并与动态时间水印渲染引擎
├── build.py                   # 跨平台通用 Python 打包脚本 (一键生成 .app 与 .exe)
├── tesla_merger.spec          # PyInstaller 打包规格配置
├── requirements.txt           # Python 依赖清单
├── .github/workflows/build.yml# GitHub Actions 自动化云端构建
├── README.md                  # 中文使用说明文档
└── README_EN.md               # 英文说明文档
```

---

## 🚀 方式一：直接运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动图形界面
无论在 macOS 还是 Windows，均通过 Python 统一启动：
```bash
python main.py
```

> **操作步骤**：
> 1. 点击【视频输入目录】右侧的【浏览...】，选中包含特斯拉视频的文件夹（系统自动开始扫描并列出所有视角）；
> 2. 【合并输出目录】默认为您的桌面，如被更改可随时点击【输出到桌面】恢复；
> 3. 根据需要勾选或取消【嵌入动态时间水印 (按录制时刻随播放递增)】；
> 4. 点击【🚀 开始合并全部视角】，稍候即可完成并可一键打开输出文件夹。

---

## 📦 方式二：一键全平台打包

运行一条命令：

```bash
python build.py
```

打包完成后，`dist/` 目录下将**直接呈现纯净的双平台应用程序**：

```text
dist/
├── TeslaVideoMerger.app       # [macOS] 原生桌面应用，双击直接运行（无终端）
└── TeslaVideoMerger.exe       # [Windows] 原生 GUI 程序，双击直接运行（无黑框）
```

> **macOS 初次打开提示安全性拦截？**  
> 在终端运行一次即可解除限制：
> ```bash
> xattr -cr dist/TeslaVideoMerger.app
> ```

---

## 🌐 方式三：云端自动化打包 (GitHub Actions)
项目内置了 `.github/workflows/build.yml`：
推送到 GitHub 仓库后，GitHub Actions 的云端 macOS 和 Windows 虚拟机将同时运行 `python build.py`，全自动生成最新的 `.app` 和 `.exe` 安装程序供直接下载使用。
