"""
Tesla Dashcam / Sentry Video Merger Core Engine
严格保证：每个视角输出且仅输出一个完整的长视频！
支持极速硬件加速动态时间水印，或者秒级纯流拷贝。
绝对不产生任何 .srt 字幕文件或多余杂质。
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

TESLA_FILENAME_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})-([a-zA-Z0-9_-]+)\.mp4$",
    re.IGNORECASE,
)

EXCLUDED_PERSPECTIVES = {"thumb", "thumbnail"}


@dataclass
class VideoClip:
    filepath: Path
    filename: str
    timestamp_str: str
    camera: str

    def __lt__(self, other: VideoClip) -> bool:
        return (self.timestamp_str, self.filename) < (other.timestamp_str, other.filename)

    @property
    def utc_epoch(self) -> int:
        try:
            dt = datetime.strptime(self.timestamp_str, "%Y-%m-%d_%H-%M-%S").replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except Exception:
            return 0


def get_default_desktop_dir() -> Path:
    home = Path.home()
    desktop = home / "Desktop"
    if desktop.exists() and desktop.is_dir():
        return desktop
    return home


def find_ffmpeg_executable() -> Optional[str]:
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path and Path(env_path).is_file():
        return str(Path(env_path).resolve())

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        meipass = Path(sys._MEIPASS)
        for name in ("ffmpeg", "ffmpeg.exe"):
            p = meipass / name
            if p.is_file() and os.access(p, os.X_OK):
                return str(p)

    base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    for candidate_dir in (base_dir, base_dir / "bin"):
        for name in ("ffmpeg", "ffmpeg.exe"):
            p = candidate_dir / name
            if p.is_file() and os.access(p, os.X_OK):
                return str(p)

    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).is_file():
            return str(Path(exe).resolve())
    except Exception:
        pass

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    return None


def get_hardware_encoder_args(ffmpeg_exe: str) -> List[str]:
    """返回高效的硬件或多线程快速编码参数。"""
    try:
        res = subprocess.run([ffmpeg_exe, "-encoders"], capture_output=True, text=True, timeout=5)
        encoders = res.stdout
        if sys.platform == "darwin" and "h264_videotoolbox" in encoders:
            # macOS 硬件加速，速度高达数百帧/秒
            return ["-c:v", "h264_videotoolbox", "-b:v", "6000k", "-pix_fmt", "yuv420p"]
        elif sys.platform == "win32" and "h264_nvenc" in encoders:
            return ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "22", "-pix_fmt", "yuv420p"]
        elif sys.platform == "win32" and "h264_qsv" in encoders:
            return ["-c:v", "h264_qsv", "-global_quality", "22", "-pix_fmt", "nv12"]
    except Exception:
        pass
    return ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p"]


def scan_tesla_directory(
    directory: Path | str,
    recursive: bool = True,
    exclude_thumb: bool = True,
) -> Tuple[Dict[str, List[VideoClip]], List[Path]]:
    dir_path = Path(directory).resolve()
    if not dir_path.is_dir():
        raise ValueError(f"指定目录不存在或不是文件夹: {dir_path}")

    camera_map: Dict[str, List[VideoClip]] = {}
    ignored_files: List[Path] = []

    iterator = dir_path.rglob("*") if recursive else dir_path.glob("*")

    for file_path in iterator:
        if not file_path.is_file():
            continue

        filename = file_path.name
        if filename.startswith("."):
            continue

        match = TESLA_FILENAME_PATTERN.match(filename)
        if not match:
            if not filename.startswith("."):
                ignored_files.append(file_path)
            continue

        timestamp_str, camera = match.groups()
        camera = camera.lower()

        if exclude_thumb and camera in EXCLUDED_PERSPECTIVES:
            ignored_files.append(file_path)
            continue

        clip = VideoClip(
            filepath=file_path.resolve(),
            filename=filename,
            timestamp_str=timestamp_str,
            camera=camera,
        )

        if camera not in camera_map:
            camera_map[camera] = []
        camera_map[camera].append(clip)

    # 每个视角下严格按录制时间戳升序排序
    for cam in camera_map:
        camera_map[cam].sort()

    return camera_map, ignored_files


def generate_output_filename(camera: str, clips: List[VideoClip]) -> str:
    """每个视角生成一个标准规范的长视频文件名。"""
    if not clips:
        return f"Tesla_{camera}.mp4"

    start_ts = clips[0].timestamp_str
    end_ts = clips[-1].timestamp_str

    if start_ts == end_ts:
        return f"Tesla_{camera}_{start_ts}.mp4"

    start_date, start_time = start_ts.split("_")
    end_date, end_time = end_ts.split("_")

    if start_date == end_date:
        return f"Tesla_{camera}_{start_ts}_to_{end_time}.mp4"
    else:
        return f"Tesla_{camera}_{start_ts}_to_{end_ts}.mp4"


def _run_subprocess(
    cmd: List[str],
    cancel_event: Optional[threading.Event] = None,
) -> Tuple[int, str]:
    extra_popen_kwargs = {}
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        extra_popen_kwargs["startupinfo"] = startupinfo
        extra_popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **extra_popen_kwargs,
    )

    while True:
        if cancel_event and cancel_event.is_set():
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            raise RuntimeError("任务已被用户取消")

        ret = process.poll()
        if ret is not None:
            break
        threading.Event().wait(0.1)

    _, stderr_data = process.communicate()
    return ret, stderr_data


def merge_camera_clips(
    camera: str,
    clips: List[VideoClip],
    output_dir: Path | str,
    ffmpeg_exe: Optional[str] = None,
    burn_timestamp: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
    cancel_event: Optional[threading.Event] = None,
) -> Path:
    """
    将单个视角（如 front, back）的所有切片合并为唯一的一个长视频文件！
    - burn_timestamp=False: 极速纯流拷贝，不重新编码，几秒钟搞定，100%原画质。
    - burn_timestamp=True: 单次硬件加速极速重绘时间水印，一次性输出唯一的一个 MP4。
    绝对不输出任何多余的 .srt 文件！
    """
    def log(msg: str):
        if log_callback:
            log_callback(msg)

    if not clips:
        raise ValueError(f"视角 '{camera}' 下没有待合并的视频切片。")

    if not ffmpeg_exe:
        ffmpeg_exe = find_ffmpeg_executable()
        if not ffmpeg_exe:
            raise RuntimeError("未检测到 FFmpeg 可执行文件。")

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    output_filename = generate_output_filename(camera, clips)
    final_output_path = out_dir / output_filename

    # 如果同名文件已存在，安全递增命名避免覆盖
    counter = 1
    base_stem = final_output_path.stem
    while final_output_path.exists():
        final_output_path = out_dir / f"{base_stem}_{counter}.mp4"
        counter += 1

    total_clips = len(clips)
    log(f"[{camera}] 开始合并 {total_clips} 个片段 -> {final_output_path.name}")

    with tempfile.TemporaryDirectory(prefix=f"tesla_{camera}_") as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        # 写入 Concat 列表
        concat_file_path = temp_dir / "concat_list.txt"
        with open(concat_file_path, "w", encoding="utf-8") as f:
            for clip in clips:
                escaped = clip.filepath.as_posix().replace("'", "'\\''")
                f.write(f"file '{escaped}'\n")

        if burn_timestamp:
            # 单进程硬件加速流水线：通过 concat 驱动，在一次 FFmpeg 执行中完成拼接与时间渲染
            start_epoch = clips[0].utc_epoch
            log(f"[{camera}] 正在进行硬件加速合并与动态时间水印渲染...")

            filter_str = (
                f"drawtext=text='%{{pts\\:gmtime\\:{start_epoch}\\:%Y-%m-%d %T}}':"
                f"x=32:y=h-th-32:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=6"
            )
            encoder_args = get_hardware_encoder_args(ffmpeg_exe)

            cmd = [
                ffmpeg_exe,
                "-hide_banner",
                "-loglevel", "error",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file_path.as_posix()),
                "-vf", filter_str,
                *encoder_args,
                "-y",
                str(final_output_path),
            ]
        else:
            # 极速流拷贝：零重编码，纯物理拼接，几秒搞定！
            log(f"[{camera}] 正在极速流拷贝合并 (纯原画质，无二次编码)...")
            cmd = [
                ffmpeg_exe,
                "-hide_banner",
                "-loglevel", "error",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file_path.as_posix()),
                "-c", "copy",
                "-y",
                str(final_output_path),
            ]

        ret, err = _run_subprocess(cmd, cancel_event)
        if ret != 0:
            if final_output_path.exists():
                try:
                    final_output_path.unlink()
                except OSError:
                    pass
            raise RuntimeError(f"FFmpeg 合并失败 [{camera}]: {err.strip()}")

    log(f"[{camera}] ✓ 合并成功！生成唯一视频: {final_output_path.name}")
    return final_output_path
