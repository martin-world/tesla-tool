#!/usr/bin/env python3
"""
Tesla Video Merger - 全平台一键编译打包脚本
执行一次同时生成 macOS 的 .app 与 Windows 的 .exe，不生成任何多余压缩包。

使用方法:
    python build.py
"""

from __future__ import annotations

import io
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"


def print_banner(text: str):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50 + "\n")


def install_requirements():
    """检查并自动安装打包所需的依赖。"""
    req_file = ROOT_DIR / "requirements.txt"
    if not req_file.exists():
        return

    print("正在检查/安装打包依赖 (requirements.txt)...")
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def clean_build_artifacts():
    """清理旧的构建临时文件。"""
    for folder in (BUILD_DIR, DIST_DIR):
        if folder.exists() and folder.is_dir():
            print(f"清理旧目录: {folder.name}/")
            shutil.rmtree(folder, ignore_errors=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def build_macos_package():
    """构建 macOS 平台 .app 应用程序"""
    print_banner("1/2 正在构建 macOS 应用: TeslaVideoMerger.app")
    current_os = platform.system()

    if current_os == "Darwin":
        spec_path = ROOT_DIR / "tesla_merger.spec"
        cache_dir = ROOT_DIR / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ["PYINSTALLER_CONFIG_DIR"] = str(cache_dir)

        import PyInstaller.__main__
        PyInstaller.__main__.run([
            "--clean",
            str(spec_path),
        ])

        # 移除裸露的 unix 命令行可执行文件，仅保留 .app 原生应用
        unix_bin = DIST_DIR / "TeslaVideoMerger"
        if unix_bin.exists():
            unix_bin.unlink()

        app_path = DIST_DIR / "TeslaVideoMerger.app"
        if app_path.exists():
            print(f"✓ 成功生成 macOS 应用: {app_path.name}")
    else:
        print("提示: 当前非 macOS 系统，跳过 .app 构建。")


def find_windows_w64_launcher() -> bytes:
    """提取官方 64 位无控制台 GUI PE 引导器。"""
    candidate_paths = [
        Path(sys.executable).parent.parent / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages" / "pip" / "_vendor" / "distlib" / "w64.exe",
        ROOT_DIR / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages" / "pip" / "_vendor" / "distlib" / "w64.exe",
    ]
    for p in candidate_paths:
        if p.is_file():
            return p.read_bytes()

    import pip
    pip_dir = Path(pip.__file__).parent
    w64_files = list(pip_dir.rglob("w64.exe"))
    if w64_files:
        return w64_files[0].read_bytes()

    import setuptools
    st_dir = Path(setuptools.__file__).parent
    gui64_files = list(st_dir.rglob("gui-64.exe"))
    if gui64_files:
        return gui64_files[0].read_bytes()

    raise FileNotFoundError("未找到 Windows 64-bit GUI 引导器二进制。")


def build_windows_package():
    """构建 Windows 平台 .exe 可执行程序"""
    print_banner("2/2 正在构建 Windows 程序: TeslaVideoMerger.exe")
    current_os = platform.system()

    if current_os == "Windows":
        spec_path = ROOT_DIR / "tesla_merger.spec"
        import PyInstaller.__main__
        PyInstaller.__main__.run([
            "--clean",
            str(spec_path),
        ])
    else:
        # 在 macOS / Linux 上：通过 Windows PE32+ GUI 引导器打包生成原生的 TeslaVideoMerger.exe
        launcher_bytes = find_windows_w64_launcher()
        shebang = b"#!pythonw.exe\r\n"

        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(ROOT_DIR / "main.py", "__main__.py")
            zf.write(ROOT_DIR / "gui.py", "gui.py")
            zf.write(ROOT_DIR / "merger.py", "merger.py")

        exe_bytes = launcher_bytes + shebang + zip_stream.getvalue()
        (DIST_DIR / "TeslaVideoMerger.exe").write_bytes(exe_bytes)

    exe_path = DIST_DIR / "TeslaVideoMerger.exe"
    if exe_path.exists():
        print(f"✓ 成功生成 Windows 程序: {exe_path.name}")


def main():
    install_requirements()
    clean_build_artifacts()

    build_macos_package()
    build_windows_package()

    print_banner("全平台打包完成！dist 目录产物")
    for item in sorted(DIST_DIR.iterdir()):
        if item.is_file():
            print(f"  👉 [文件] {item.name}")
        elif item.is_dir():
            print(f"  👉 [应用] {item.name}")
    print("\n产物纯净，无任何多余压缩包！")


if __name__ == "__main__":
    main()
