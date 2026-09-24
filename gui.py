"""
Tesla Dashcam / Sentry Video Merger GUI
Modern, cross-platform Tkinter GUI with bilingual (Chinese & English) switching support.
Strictly ensures one merged video file per camera angle.
"""

from __future__ import annotations

import locale
import os
import platform
import queue
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Dict, List, Optional

from merger import (
    VideoClip,
    find_ffmpeg_executable,
    generate_output_filename,
    get_default_desktop_dir,
    merge_camera_clips,
    scan_tesla_directory,
)

# Bilingual dictionary
I18N = {
    "zh": {
        "app_title": "特斯拉行车记录仪/哨兵视频合并工具",
        "window_title": "特斯拉视频合并工具 (Tesla Video Merger)",
        "lang_label": "🌐 语言 / Language:",
        "paths_options_frame": " 路径与选项 ",
        "input_dir_label": "视频输入目录:",
        "output_dir_label": "合并输出目录:",
        "browse": "浏览...",
        "output_to_desktop": "输出到桌面",
        "burn_timestamp": "嵌入动态时间水印 (按录制时刻随播放递增)",
        "recursive_scan": "递归扫描子文件夹",
        "filter_thumb": "排除低清缩略图 (thumb)",
        "tree_frame": " 检测到的视角与待输出的长视频 (每个视角生成一个长视频) ",
        "col_camera": "视角代号",
        "col_count": "切片数量",
        "col_span": "时间跨度 (从 -> 到)",
        "col_target": "输出的长视频文件 (每个视角唯一)",
        "btn_merge": "🚀 开始合并 (各视角分别生成长视频)",
        "btn_cancel": "⏹ 取消任务",
        "btn_open_out": "📂 打开输出目录",
        "log_frame": " 执行日志与明细 ",
        "ready": "就绪，请选择特斯拉视频文件夹",
        "scanning": "正在自动扫描目录中的特斯拉视频文件...",
        "scan_finished": "扫描完成: 发现 {cams} 个视角，各将输出 1 个长视频 (共计 {clips} 个片段)。",
        "scan_log": "扫描完成: 发现视角 {cams}，每个视角将合并输出 1 个长视频。",
        "scan_empty": "未在目录中找到符合特斯拉格式的有效视频。",
        "scan_empty_log": "扫描完毕: 未找到匹配 YYYY-MM-DD_HH-MM-SS-<camera>.mp4 的有效视频文件。",
        "filtered_log": "已自动排除不符合格式或缩略图文件 {count} 个。",
        "merging_start": "开始合并各视角视频，共 {cams} 个视角 (各输出 1 个长视频，时间水印: {ts_status})...",
        "merging_angle": "正在处理视角 [{idx}/{total}]: {cam} (合并为 1 个长视频)...",
        "cancel_confirm_title": "确认",
        "cancel_confirm_msg": "确定要中断正在进行的视频合并任务吗？",
        "cancel_sent": "已发送取消请求，正在终止任务...",
        "cancelling": "正在取消任务...",
        "cancelled": "视频合并任务已中断取消。",
        "cancelled_status": "合并已被取消。",
        "cancelled_alert": "合并任务已取消。",
        "all_failed_status": "合并全部失败，请查看日志。",
        "all_failed_title": "合并失败",
        "all_failed_msg": "视角合并出现错误，详细原因请查看日志窗口。\n{error}",
        "complete_status": "全部合并完成！每个视角对应一个长视频。",
        "complete_alert_title": "合并完成",
        "complete_msg": "🎉 合并完成！已成功按视角生成 {count} 个长视频文件。",
        "failed_notice": "\n另外有 {count} 个视角处理失败。",
        "open_folder_prompt": "\n\n是否立即打开输出文件夹查看？",
        "reset_desktop_log": "已将合并输出目录设置为桌面: {path}",
        "ffmpeg_ok": "已检测到 FFmpeg 引擎: {exe}",
        "ffmpeg_warn": "警告: 未在系统中检测到 FFmpeg，请检查安装。",
        "ffmpeg_missing_title": "缺少 FFmpeg",
        "ffmpeg_missing_msg": "未检测到 FFmpeg 可执行文件。\n请确保已配置 FFmpeg。",
        "select_input_title": "选择包含特斯拉视频的文件夹",
        "select_output_title": "选择合并长视频的输出文件夹",
        "no_clips_warn": "当前没有检测到可合并的视频切片，请先选择有效目录。",
        "no_output_warn": "请选择合并输出目录。",
        "no_output_dir_info": "输出目录尚未生成或不存在。",
        "path_not_found": "输入的路径不存在或不是文件夹: {path}",
        "open_folder_fail": "无法自动打开文件夹: {error}",
        "clip_unit": "{count} 个片段",
        "enabled": "开启",
        "disabled": "关闭",
        "alert_tip": "提示",
        "alert_error": "错误",
    },
    "en": {
        "app_title": "Tesla Dashcam & Sentry Video Merger",
        "window_title": "Tesla Video Merger",
        "lang_label": "🌐 Language / 语言:",
        "paths_options_frame": " Paths & Options ",
        "input_dir_label": "Video Input Dir:",
        "output_dir_label": "Merge Output Dir:",
        "browse": "Browse...",
        "output_to_desktop": "To Desktop",
        "burn_timestamp": "Burn dynamic timestamp watermark (Increments with playback)",
        "recursive_scan": "Recursive scan subfolders",
        "filter_thumb": "Exclude thumbnails (thumb)",
        "tree_frame": " Detected Perspectives & Output Videos (One video per perspective) ",
        "col_camera": "Perspective",
        "col_count": "Clip Count",
        "col_span": "Time Span (From -> To)",
        "col_target": "Output Long Video (Unique per perspective)",
        "btn_merge": "🚀 Start Merge (One video per perspective)",
        "btn_cancel": "⏹ Cancel Task",
        "btn_open_out": "📂 Open Output Folder",
        "log_frame": " Execution Logs & Details ",
        "ready": "Ready. Please select a Tesla video folder.",
        "scanning": "Scanning directory for Tesla video clips...",
        "scan_finished": "Scan complete: Found {cams} perspectives, each will output 1 video ({clips} clips total).",
        "scan_log": "Scan complete: Found perspectives {cams}, each will output 1 merged video.",
        "scan_empty": "No valid Tesla video clips found in the selected directory.",
        "scan_empty_log": "Scan complete: No files matching YYYY-MM-DD_HH-MM-SS-<camera>.mp4.",
        "filtered_log": "Excluded {count} non-standard or thumbnail files.",
        "merging_start": "Starting merge for {cams} perspectives (1 video each, timestamp: {ts_status})...",
        "merging_angle": "Processing perspective [{idx}/{total}]: {cam} (Merging into 1 video)...",
        "cancel_confirm_title": "Confirm",
        "cancel_confirm_msg": "Are you sure you want to cancel the merging task?",
        "cancel_sent": "Cancellation requested, stopping task...",
        "cancelling": "Cancelling task...",
        "cancelled": "Merging task was cancelled.",
        "cancelled_status": "Merge was cancelled.",
        "cancelled_alert": "Merge task has been cancelled.",
        "all_failed_status": "All merges failed, please check the log.",
        "all_failed_title": "Merge Failed",
        "all_failed_msg": "Failed to merge perspectives. Details in the log window.\n{error}",
        "complete_status": "All merges completed! One long video per perspective.",
        "complete_alert_title": "Merge Completed",
        "complete_msg": "🎉 Merge complete! Successfully generated {count} video files.",
        "failed_notice": "\nAdditionally, {count} perspectives failed.",
        "open_folder_prompt": "\n\nWould you like to open the output folder now?",
        "reset_desktop_log": "Reset output directory to Desktop: {path}",
        "ffmpeg_ok": "Detected FFmpeg engine: {exe}",
        "ffmpeg_warn": "Warning: FFmpeg not detected in system. Please verify installation.",
        "ffmpeg_missing_title": "FFmpeg Missing",
        "ffmpeg_missing_msg": "FFmpeg executable not found.\nPlease ensure FFmpeg is configured.",
        "select_input_title": "Select Tesla Video Folder",
        "select_output_title": "Select Output Folder for Merged Videos",
        "no_clips_warn": "No video clips detected. Please select a valid folder first.",
        "no_output_warn": "Please select an output directory.",
        "no_output_dir_info": "Output directory does not exist yet.",
        "path_not_found": "Path does not exist or is not a directory: {path}",
        "open_folder_fail": "Cannot open folder automatically: {error}",
        "clip_unit": "{count} clips",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "alert_tip": "Notice",
        "alert_error": "Error",
    }
}


def open_folder_in_explorer(folder_path: Path | str) -> None:
    """Opens directory in native Finder / Explorer."""
    p = str(Path(folder_path).resolve())
    current_os = platform.system()
    try:
        if current_os == "Darwin":
            subprocess.run(["open", p], check=False)
        elif current_os == "Windows":
            os.startfile(p)
        else:
            subprocess.run(["xdg-open", p], check=False)
    except Exception as e:
        messagebox.showwarning("Notice", f"Cannot open folder: {e}")


class TeslaMergerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root

        # Auto-detect language
        self.current_lang = "zh"
        try:
            loc = locale.getdefaultlocale()[0]
            if loc and not loc.lower().startswith("zh"):
                self.current_lang = "en"
        except Exception:
            self.current_lang = "zh"

        self.root.title(self.t("window_title"))
        self.root.geometry("880x700")
        self.root.minsize(760, 580)

        # Style & Theme
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        if "aqua" in available_themes and platform.system() == "Darwin":
            self.style.theme_use("aqua")
        elif "vista" in available_themes and platform.system() == "Windows":
            self.style.theme_use("vista")
        elif "clam" in available_themes:
            self.style.theme_use("clam")

        # State Variables
        self.input_dir_var = tk.StringVar(value="")
        self.output_dir_var = tk.StringVar(value=str(get_default_desktop_dir()))
        self.recursive_var = tk.BooleanVar(value=True)
        self.filter_thumb_var = tk.BooleanVar(value=True)
        self.burn_timestamp_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value=self.t("ready"))

        self.scanned_camera_map: Dict[str, List[VideoClip]] = {}
        self.ignored_files: List[Path] = []
        self.cancel_event: Optional[threading.Event] = None
        self.is_processing = False

        self.msg_queue: queue.Queue = queue.Queue()

        self._create_widgets()
        self._update_ui_texts()
        self._check_ffmpeg_environment()
        self._process_queue_messages()

    def t(self, key: str, **kwargs) -> str:
        """Fetch localized string with optional formatting."""
        lang_dict = I18N.get(self.current_lang, I18N["zh"])
        template = lang_dict.get(key, I18N["zh"].get(key, key))
        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="14")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 0. Top Bar (App Title & Language Switcher)
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        self.lbl_app_title = ttk.Label(top_bar, text="", font=("Helvetica", 13, "bold"))
        self.lbl_app_title.pack(side=tk.LEFT)

        lang_frame = ttk.Frame(top_bar)
        lang_frame.pack(side=tk.RIGHT)

        self.lbl_lang = ttk.Label(lang_frame, text="")
        self.lbl_lang.pack(side=tk.LEFT, padx=(0, 6))

        self.lang_combobox = ttk.Combobox(
            lang_frame,
            values=["中文", "English"],
            state="readonly",
            width=9,
        )
        self.lang_combobox.set("中文" if self.current_lang == "zh" else "English")
        self.lang_combobox.pack(side=tk.LEFT)
        self.lang_combobox.bind("<<ComboboxSelected>>", self._on_language_change)

        # 1. Paths & Options Frame
        self.config_frame = ttk.LabelFrame(main_frame, text="", padding="10")
        self.config_frame.pack(fill=tk.X, pady=(0, 10))

        # Video Input Directory
        self.lbl_input_dir = ttk.Label(self.config_frame, text="")
        self.lbl_input_dir.grid(row=0, column=0, sticky=tk.W, pady=4)

        input_entry = ttk.Entry(self.config_frame, textvariable=self.input_dir_var)
        input_entry.grid(row=0, column=1, sticky=tk.EW, padx=8, pady=4)
        input_entry.bind("<Return>", lambda e: self._start_scan())
        input_entry.bind("<FocusOut>", lambda e: self._on_input_focus_out())

        self.btn_browse_in = ttk.Button(self.config_frame, text="", width=10, command=self._browse_input_dir)
        self.btn_browse_in.grid(row=0, column=2, padx=(0, 4), pady=4)

        # Merge Output Directory
        self.lbl_output_dir = ttk.Label(self.config_frame, text="")
        self.lbl_output_dir.grid(row=1, column=0, sticky=tk.W, pady=4)

        output_entry = ttk.Entry(self.config_frame, textvariable=self.output_dir_var)
        output_entry.grid(row=1, column=1, sticky=tk.EW, padx=8, pady=4)

        self.btn_browse_out = ttk.Button(self.config_frame, text="", width=10, command=self._browse_output_dir)
        self.btn_browse_out.grid(row=1, column=2, padx=(0, 4), pady=4)

        self.btn_to_desktop = ttk.Button(self.config_frame, text="", width=12, command=self._reset_output_dir)
        self.btn_to_desktop.grid(row=1, column=3, pady=4)

        # Options Checkboxes
        options_frame = ttk.Frame(self.config_frame)
        options_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W, pady=(6, 0))

        self.chk_burn_ts = ttk.Checkbutton(
            options_frame,
            text="",
            variable=self.burn_timestamp_var,
        )
        self.chk_burn_ts.pack(side=tk.LEFT, padx=(0, 16))

        self.chk_recursive = ttk.Checkbutton(
            options_frame,
            text="",
            variable=self.recursive_var,
        )
        self.chk_recursive.pack(side=tk.LEFT, padx=(0, 16))

        self.chk_filter_thumb = ttk.Checkbutton(
            options_frame,
            text="",
            variable=self.filter_thumb_var,
        )
        self.chk_filter_thumb.pack(side=tk.LEFT)

        self.config_frame.columnconfigure(1, weight=1)

        # 2. Camera Perspectives & Output Long Video Preview
        self.tree_frame = ttk.LabelFrame(main_frame, text="", padding="8")
        self.tree_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        columns = ("camera", "count", "time_span", "target_file")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=5)

        self.tree.column("camera", width=120, anchor=tk.CENTER)
        self.tree.column("count", width=110, anchor=tk.CENTER)
        self.tree.column("time_span", width=260, anchor=tk.CENTER)
        self.tree.column("target_file", width=280, anchor=tk.W)

        tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 3. Actions & Status Bar
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 8))

        self.btn_merge = ttk.Button(
            action_frame,
            text="",
            command=self._start_merge,
            state=tk.DISABLED,
        )
        self.btn_merge.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_cancel = ttk.Button(
            action_frame,
            text="",
            command=self._cancel_merge,
            state=tk.DISABLED,
        )
        self.btn_cancel.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_open_out = ttk.Button(
            action_frame,
            text="",
            command=self._open_output_folder,
        )
        self.btn_open_out.pack(side=tk.RIGHT)

        # Progress bar & Status label
        self.progress_bar = ttk.Progressbar(main_frame, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))

        status_lbl = ttk.Label(main_frame, textvariable=self.status_var, font=("Helvetica", 11, "bold"))
        status_lbl.pack(anchor=tk.W, pady=(0, 6))

        # 4. Execution Logs Panel
        self.log_frame = ttk.LabelFrame(main_frame, text="", padding="6")
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = ScrolledText(
            self.log_frame,
            height=8,
            wrap=tk.WORD,
            font=("Courier", 10) if platform.system() == "Darwin" else ("Consolas", 9),
            state=tk.DISABLED,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config("info", foreground="#1f2937")
        self.log_text.tag_config("success", foreground="#059669")
        self.log_text.tag_config("warn", foreground="#d97706")
        self.log_text.tag_config("error", foreground="#dc2626")

    def _on_language_change(self, event=None):
        selected = self.lang_combobox.get()
        new_lang = "zh" if selected == "中文" else "en"
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            self._update_ui_texts()
            # If clips already scanned, re-render tree items to update unit string
            if self.scanned_camera_map:
                self._refresh_tree_display()

    def _update_ui_texts(self):
        """Refreshes all visible UI labels and button texts to the active language."""
        self.root.title(self.t("window_title"))
        self.lbl_app_title.configure(text=self.t("app_title"))
        self.lbl_lang.configure(text=self.t("lang_label"))

        self.config_frame.configure(text=self.t("paths_options_frame"))
        self.lbl_input_dir.configure(text=self.t("input_dir_label"))
        self.lbl_output_dir.configure(text=self.t("output_dir_label"))
        self.btn_browse_in.configure(text=self.t("browse"))
        self.btn_browse_out.configure(text=self.t("browse"))
        self.btn_to_desktop.configure(text=self.t("output_to_desktop"))

        self.chk_burn_ts.configure(text=self.t("burn_timestamp"))
        self.chk_recursive.configure(text=self.t("recursive_scan"))
        self.chk_filter_thumb.configure(text=self.t("filter_thumb"))

        self.tree_frame.configure(text=self.t("tree_frame"))
        self.tree.heading("camera", text=self.t("col_camera"))
        self.tree.heading("count", text=self.t("col_count"))
        self.tree.heading("time_span", text=self.t("col_span"))
        self.tree.heading("target_file", text=self.t("col_target"))

        self.btn_merge.configure(text=self.t("btn_merge"))
        self.btn_cancel.configure(text=self.t("btn_cancel"))
        self.btn_open_out.configure(text=self.t("btn_open_out"))

        self.log_frame.configure(text=self.t("log_frame"))

        # Update status if in ready state
        if not self.is_processing and not self.scanned_camera_map:
            self.status_var.set(self.t("ready"))

    def _refresh_tree_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for cam, clips in sorted(self.scanned_camera_map.items()):
            start_ts = clips[0].timestamp_str
            end_ts = clips[-1].timestamp_str
            time_span = f"{start_ts} -> {end_ts.split('_')[-1]}" if "_" in end_ts else f"{start_ts} -> {end_ts}"
            target_name = generate_output_filename(cam, clips)
            count_str = self.t("clip_unit", count=len(clips))
            self.tree.insert("", tk.END, values=(cam, count_str, time_span, target_name))

    def _log(self, text: str, tag: str = "info"):
        now_str = datetime.now().strftime("%H:%M:%S")
        self.msg_queue.put(("log", f"[{now_str}] {text}\n", tag))

    def _process_queue_messages(self):
        try:
            while True:
                msg_type, data, *extra = self.msg_queue.get_nowait()
                if msg_type == "log":
                    tag = extra[0] if extra else "info"
                    self.log_text.configure(state=tk.NORMAL)
                    self.log_text.insert(tk.END, data, tag)
                    self.log_text.see(tk.END)
                    self.log_text.configure(state=tk.DISABLED)
                elif msg_type == "status":
                    self.status_var.set(data)
                elif msg_type == "progress":
                    self.progress_bar["value"] = data
                elif msg_type == "finish_scan":
                    self._on_scan_finished(data)
                elif msg_type == "finish_merge":
                    self._on_merge_finished(data)
        except queue.Empty:
            pass
        finally:
            self.root.after(80, self._process_queue_messages)

    def _check_ffmpeg_environment(self):
        exe = find_ffmpeg_executable()
        if exe:
            self._log(self.t("ffmpeg_ok", exe=exe), "success")
        else:
            self._log(self.t("ffmpeg_warn"), "error")
            messagebox.showerror(
                self.t("ffmpeg_missing_title"),
                self.t("ffmpeg_missing_msg"),
            )

    def _browse_input_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_input_title"))
        if folder:
            self.input_dir_var.set(folder)
            self._start_scan()

    def _on_input_focus_out(self):
        p = self.input_dir_var.get().strip()
        if p and Path(p).is_dir() and not self.scanned_camera_map:
            self._start_scan()

    def _browse_output_dir(self):
        folder = filedialog.askdirectory(title=self.t("select_output_title"))
        if folder:
            self.output_dir_var.set(folder)

    def _reset_output_dir(self):
        desktop = get_default_desktop_dir()
        self.output_dir_var.set(str(desktop))
        self._log(self.t("reset_desktop_log", path=desktop), "info")

    def _open_output_folder(self):
        out_dir = self.output_dir_var.get().strip()
        if out_dir and Path(out_dir).is_dir():
            open_folder_in_explorer(out_dir)
        else:
            messagebox.showinfo(self.t("alert_tip"), self.t("no_output_dir_info"))

    def _start_scan(self):
        input_dir = self.input_dir_var.get().strip()
        if not input_dir:
            return
        if not Path(input_dir).is_dir():
            messagebox.showerror(self.t("alert_error"), self.t("path_not_found", path=input_dir))
            return

        self.status_var.set(self.t("scanning"))
        self._log(f"{self.t('scanning')} ({input_dir})")
        self.btn_merge.configure(state=tk.DISABLED)

        for row in self.tree.get_children():
            self.tree.delete(row)

        recursive = self.recursive_var.get()
        exclude_thumb = self.filter_thumb_var.get()

        def scan_worker():
            try:
                c_map, ignored = scan_tesla_directory(
                    input_dir, recursive=recursive, exclude_thumb=exclude_thumb
                )
                self.msg_queue.put(("finish_scan", (c_map, ignored)))
            except Exception as e:
                self.msg_queue.put(("log", f"Scan error: {e}\n", "error"))
                self.msg_queue.put(("status", "Scan failed"))

        threading.Thread(target=scan_worker, daemon=True).start()

    def _on_scan_finished(self, result):
        c_map, ignored = result
        self.scanned_camera_map = c_map
        self.ignored_files = ignored

        total_valid_clips = sum(len(clips) for clips in c_map.values())

        if not c_map:
            self.status_var.set(self.t("scan_empty"))
            self._log(self.t("scan_empty_log"), "warn")
            if ignored:
                self._log(self.t("filtered_log", count=len(ignored)), "warn")
            self.btn_merge.configure(state=tk.DISABLED)
            return

        self._refresh_tree_display()

        self.status_var.set(self.t("scan_finished", cams=len(c_map), clips=total_valid_clips))
        self._log(self.t("scan_log", cams=list(c_map.keys())), "success")
        if ignored:
            self._log(self.t("filtered_log", count=len(ignored)), "info")

        self.btn_merge.configure(state=tk.NORMAL)

    def _start_merge(self):
        if not self.scanned_camera_map:
            messagebox.showwarning(self.t("alert_tip"), self.t("no_clips_warn"))
            return

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning(self.t("alert_tip"), self.t("no_output_warn"))
            return

        ffmpeg_exe = find_ffmpeg_executable()
        if not ffmpeg_exe:
            messagebox.showerror(self.t("alert_error"), self.t("ffmpeg_missing_msg"))
            return

        self.is_processing = True
        self.cancel_event = threading.Event()
        self.btn_merge.configure(state=tk.DISABLED)
        self.btn_cancel.configure(state=tk.NORMAL)
        self.progress_bar["value"] = 0

        cameras = list(self.scanned_camera_map.keys())
        total_cams = len(cameras)
        camera_map_copy = {k: list(v) for k, v in self.scanned_camera_map.items()}
        burn_ts = self.burn_timestamp_var.get()
        ts_desc = self.t("enabled") if burn_ts else self.t("disabled")

        self._log(self.t("merging_start", cams=total_cams, ts_status=ts_desc), "info")

        def merge_worker():
            merged_results = []
            failed_results = []

            for idx, cam in enumerate(cameras, start=1):
                if self.cancel_event.is_set():
                    break

                clips = camera_map_copy[cam]
                self.msg_queue.put(("status", self.t("merging_angle", idx=idx, total=total_cams, cam=cam)))

                try:
                    out_path = merge_camera_clips(
                        camera=cam,
                        clips=clips,
                        output_dir=output_dir,
                        ffmpeg_exe=ffmpeg_exe,
                        burn_timestamp=burn_ts,
                        log_callback=lambda msg: self.msg_queue.put(("log", msg + "\n", "info")),
                        cancel_event=self.cancel_event,
                    )
                    merged_results.append((cam, out_path))
                except Exception as e:
                    failed_results.append((cam, str(e)))
                    self.msg_queue.put(("log", f"[{cam}] Error: {e}\n", "error"))

                pct = int((idx / total_cams) * 100)
                self.msg_queue.put(("progress", pct))

            final_pct = 100 if not self.cancel_event.is_set() else 0
            self.msg_queue.put(("progress", final_pct))
            self.msg_queue.put(("finish_merge", (merged_results, failed_results, self.cancel_event.is_set())))

        threading.Thread(target=merge_worker, daemon=True).start()

    def _cancel_merge(self):
        if self.cancel_event and not self.cancel_event.is_set():
            if messagebox.askyesno(self.t("cancel_confirm_title"), self.t("cancel_confirm_msg")):
                self.cancel_event.set()
                self._log(self.t("cancel_sent"), "warn")
                self.status_var.set(self.t("cancelling"))

    def _on_merge_finished(self, result):
        merged_results, failed_results, was_cancelled = result
        self.is_processing = False
        self.btn_cancel.configure(state=tk.DISABLED)
        self.btn_merge.configure(state=tk.NORMAL)

        if was_cancelled:
            self.status_var.set(self.t("cancelled_status"))
            self._log(self.t("cancelled"), "warn")
            messagebox.showinfo(self.t("alert_tip"), self.t("cancelled_alert"))
            return

        if failed_results and not merged_results:
            self.status_var.set(self.t("all_failed_status"))
            messagebox.showerror(
                self.t("all_failed_title"),
                self.t("all_failed_msg", error=failed_results[0][1]),
            )
            return

        success_cams = [c for c, _ in merged_results]
        msg = self.t("complete_msg", count=len(success_cams))
        if failed_results:
            msg += self.t("failed_notice", count=len(failed_results))

        self.status_var.set(self.t("complete_status"))
        self._log(msg, "success")

        prompt = msg + self.t("open_folder_prompt")
        if messagebox.askyesno(self.t("complete_alert_title"), prompt):
            self._open_output_folder()


def run_gui():
    root = tk.Tk()
    app = TeslaMergerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
