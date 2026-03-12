"""
Platform detection utilities for Android/Termux compatibility.

This module provides helpers to detect the runtime environment and
apply appropriate platform-specific defaults and workarounds.
"""

import os
import sys
from pathlib import Path


def is_termux() -> bool:
    """Detect whether the code is running inside Termux on Android.

    Termux sets the ``TERMUX_VERSION`` environment variable and its
    prefix directory (``$PREFIX``) lives under
    ``/data/data/com.termux/files``.

    Returns:
        True if running inside Termux, False otherwise.
    """
    if os.environ.get("TERMUX_VERSION"):
        return True
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix


def is_android() -> bool:
    """Detect whether the code is running on an Android device.

    This covers both plain Android (e.g. Pydroid, Termux, QPython) and
    environments where the Android build property file is present.

    Returns:
        True if running on Android, False otherwise.
    """
    if is_termux():
        return True
    # Check for Android-specific paths/properties
    return (
        os.path.exists("/system/build.prop")
        or os.path.exists("/system/app")
        or os.environ.get("ANDROID_ROOT") is not None
        or os.environ.get("ANDROID_DATA") is not None
    )


def supports_fork() -> bool:
    """Return True if the current platform supports ``os.fork()``.

    ``os.fork()`` is a POSIX-only call that is not available on Windows
    and may raise ``OSError`` on some restricted Android environments.

    Returns:
        True if ``os.fork`` is available and expected to work.
    """
    return hasattr(os, "fork") and sys.platform != "win32"


def get_default_data_dir() -> str:
    """Return a platform-appropriate default data storage directory.

    On Termux the conventional location is inside the Termux home tree
    rather than a path relative to the current working directory.

    Returns:
        Absolute path string for the default data directory.
    """
    if is_termux():
        home = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
        return str(home / ".wifi-densepose" / "data")
    return "./data"


def get_default_log_dir() -> str:
    """Return a platform-appropriate default log directory.

    Returns:
        Absolute path string for the default log directory.
    """
    if is_termux():
        home = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
        return str(home / ".wifi-densepose" / "logs")
    return "./logs"


def get_default_model_dir() -> str:
    """Return a platform-appropriate default model storage directory.

    Returns:
        Absolute path string for the default model directory.
    """
    if is_termux():
        home = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
        return str(home / ".wifi-densepose" / "models")
    return "./models"


def get_default_temp_dir() -> str:
    """Return a platform-appropriate default temporary directory.

    Returns:
        Absolute path string for the default temp directory.
    """
    if is_termux():
        home = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
        return str(home / ".wifi-densepose" / "temp")
    return "./temp"


def get_default_backup_dir() -> str:
    """Return a platform-appropriate default backup directory.

    Returns:
        Absolute path string for the default backup directory.
    """
    if is_termux():
        home = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
        return str(home / ".wifi-densepose" / "backups")
    return "./backups"


def get_default_sqlite_fallback_path() -> str:
    """Return a platform-appropriate SQLite fallback database path.

    Returns:
        Absolute path string for the SQLite fallback database.
    """
    if is_termux():
        home = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
        return str(home / ".wifi-densepose" / "data" / "wifi_densepose_fallback.db")
    return "./data/wifi_densepose_fallback.db"


def get_platform_info() -> dict:
    """Return a dictionary with detected platform information.

    Returns:
        Dict containing platform details useful for diagnostics.
    """
    return {
        "platform": sys.platform,
        "is_android": is_android(),
        "is_termux": is_termux(),
        "supports_fork": supports_fork(),
        "python_version": sys.version,
        "home_dir": str(Path.home()),
        "termux_prefix": os.environ.get("PREFIX"),
        "android_root": os.environ.get("ANDROID_ROOT"),
    }
