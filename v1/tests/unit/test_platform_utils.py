"""Unit tests for the Android/Termux platform detection utility."""

import os
import sys
from unittest.mock import patch

import pytest

from src.utils.platform import (
    get_default_backup_dir,
    get_default_data_dir,
    get_default_log_dir,
    get_default_model_dir,
    get_default_sqlite_fallback_path,
    get_default_temp_dir,
    get_platform_info,
    is_android,
    is_termux,
    supports_fork,
)


class TestIsTermux:
    """Tests for is_termux()."""

    def test_returns_true_when_termux_version_env_set(self):
        with patch.dict(os.environ, {"TERMUX_VERSION": "0.118"}, clear=False):
            assert is_termux() is True

    def test_returns_true_when_prefix_contains_termux(self):
        with patch.dict(os.environ, {"PREFIX": "/data/data/com.termux/files/usr"}, clear=False):
            assert is_termux() is True

    def test_returns_false_on_normal_linux(self):
        env = {k: v for k, v in os.environ.items() if k not in ("TERMUX_VERSION", "PREFIX")}
        with patch.dict(os.environ, env, clear=True):
            assert is_termux() is False

    def test_returns_false_when_prefix_is_standard(self):
        env = {k: v for k, v in os.environ.items() if k not in ("TERMUX_VERSION",)}
        env["PREFIX"] = "/usr/local"
        with patch.dict(os.environ, env, clear=True):
            assert is_termux() is False


class TestIsAndroid:
    """Tests for is_android()."""

    def test_returns_true_when_termux(self):
        with patch.dict(os.environ, {"TERMUX_VERSION": "0.118"}, clear=False):
            assert is_android() is True

    def test_returns_true_when_android_root_env(self):
        env = {k: v for k, v in os.environ.items() if k not in ("TERMUX_VERSION", "PREFIX")}
        env["ANDROID_ROOT"] = "/system"
        with patch.dict(os.environ, env, clear=True):
            assert is_android() is True

    def test_returns_true_when_android_data_env(self):
        env = {k: v for k, v in os.environ.items() if k not in ("TERMUX_VERSION", "PREFIX")}
        env["ANDROID_DATA"] = "/data"
        with patch.dict(os.environ, env, clear=True):
            assert is_android() is True

    def test_returns_false_on_normal_platform(self):
        # Patch filesystem checks and clear Android env vars
        env = {
            k: v for k, v in os.environ.items()
            if k not in ("TERMUX_VERSION", "PREFIX", "ANDROID_ROOT", "ANDROID_DATA")
        }
        with patch.dict(os.environ, env, clear=True), patch("os.path.exists", return_value=False):
            assert is_android() is False


class TestSupportsFork:
    """Tests for supports_fork()."""

    def test_returns_false_on_windows(self):
        with patch.object(sys, "platform", "win32"):
            assert supports_fork() is False

    def test_returns_true_on_posix_with_fork(self):
        with patch.object(sys, "platform", "linux"), \
             patch.object(os, "fork", create=True, new=lambda: 0):
            assert supports_fork() is True

    def test_returns_false_when_os_fork_missing(self):
        original_fork = getattr(os, "fork", None)
        try:
            if hasattr(os, "fork"):
                delattr(os, "fork")  # type: ignore[attr-defined]
            with patch.object(sys, "platform", "linux"):
                assert supports_fork() is False
        finally:
            if original_fork is not None:
                os.fork = original_fork  # type: ignore[attr-defined]


class TestDefaultDirs:
    """Tests for platform-aware default directory helpers."""

    def _clear_env(self):
        """Return env dict without Termux-specific keys."""
        return {
            k: v for k, v in os.environ.items()
            if k not in ("TERMUX_VERSION", "PREFIX", "HOME")
        }
    def test_data_dir_non_termux(self):
        env = self._clear_env()
        with patch.dict(os.environ, env, clear=True):
            assert get_default_data_dir() == "./data"

    def test_log_dir_non_termux(self):
        env = self._clear_env()
        with patch.dict(os.environ, env, clear=True):
            assert get_default_log_dir() == "./logs"

    def test_model_dir_non_termux(self):
        env = self._clear_env()
        with patch.dict(os.environ, env, clear=True):
            assert get_default_model_dir() == "./models"

    def test_temp_dir_non_termux(self):
        env = self._clear_env()
        with patch.dict(os.environ, env, clear=True):
            assert get_default_temp_dir() == "./temp"

    def test_backup_dir_non_termux(self):
        env = self._clear_env()
        with patch.dict(os.environ, env, clear=True):
            assert get_default_backup_dir() == "./backups"

    def test_sqlite_fallback_path_non_termux(self):
        env = self._clear_env()
        with patch.dict(os.environ, env, clear=True):
            assert get_default_sqlite_fallback_path() == "./data/wifi_densepose_fallback.db"

    def test_data_dir_termux(self):
        with patch.dict(
            os.environ,
            {"TERMUX_VERSION": "0.118", "HOME": "/data/data/com.termux/files/home"},
            clear=False,
        ):
            result = get_default_data_dir()
            assert result.endswith("/.wifi-densepose/data")
            assert "com.termux" in result

    def test_log_dir_termux(self):
        with patch.dict(
            os.environ,
            {"TERMUX_VERSION": "0.118", "HOME": "/data/data/com.termux/files/home"},
            clear=False,
        ):
            result = get_default_log_dir()
            assert result.endswith("/.wifi-densepose/logs")

    def test_model_dir_termux(self):
        with patch.dict(
            os.environ,
            {"TERMUX_VERSION": "0.118", "HOME": "/data/data/com.termux/files/home"},
            clear=False,
        ):
            result = get_default_model_dir()
            assert result.endswith("/.wifi-densepose/models")

    def test_temp_dir_termux(self):
        with patch.dict(
            os.environ,
            {"TERMUX_VERSION": "0.118", "HOME": "/data/data/com.termux/files/home"},
            clear=False,
        ):
            result = get_default_temp_dir()
            assert result.endswith("/.wifi-densepose/temp")

    def test_backup_dir_termux(self):
        with patch.dict(
            os.environ,
            {"TERMUX_VERSION": "0.118", "HOME": "/data/data/com.termux/files/home"},
            clear=False,
        ):
            result = get_default_backup_dir()
            assert result.endswith("/.wifi-densepose/backups")

    def test_sqlite_fallback_path_termux(self):
        with patch.dict(
            os.environ,
            {"TERMUX_VERSION": "0.118", "HOME": "/data/data/com.termux/files/home"},
            clear=False,
        ):
            result = get_default_sqlite_fallback_path()
            assert result.endswith("/.wifi-densepose/data/wifi_densepose_fallback.db")


class TestGetPlatformInfo:
    """Tests for get_platform_info()."""

    def test_returns_dict_with_required_keys(self):
        info = get_platform_info()
        assert "platform" in info
        assert "is_android" in info
        assert "is_termux" in info
        assert "supports_fork" in info
        assert "python_version" in info
        assert "home_dir" in info

    def test_platform_matches_sys_platform(self):
        info = get_platform_info()
        assert info["platform"] == sys.platform

    def test_is_termux_consistent(self):
        info = get_platform_info()
        assert info["is_termux"] == is_termux()

    def test_is_android_consistent(self):
        info = get_platform_info()
        assert info["is_android"] == is_android()
