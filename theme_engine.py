"""Theme engine for managing dark/light mode color schemes and persistence."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path


class ThemeEngine:
    """Manages dark/light mode color schemes and persistence."""

    DARK_SCHEME: dict[str, str] = {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_card": "#0f3460",
        "fg_primary": "#e0e0e0",
        "fg_secondary": "#a0a0a0",
        "accent": "#0096c7",
        "error": "#e63946",
        "success": "#2a9d8f",
        "border": "#2a2a4a",
    }

    LIGHT_SCHEME: dict[str, str] = {
        "bg_primary": "#f8f9fa",
        "bg_secondary": "#ffffff",
        "bg_card": "#ffffff",
        "fg_primary": "#212529",
        "fg_secondary": "#6c757d",
        "accent": "#0077b6",
        "error": "#dc3545",
        "success": "#198754",
        "border": "#dee2e6",
    }

    def __init__(self, config_path: str | None = None):
        """Initialize with optional config file path for persistence.

        Args:
            config_path: Path to the theme config JSON file.
                         Defaults to ~/.messagecipher/theme.json.
        """
        if config_path is None:
            self._config_path = Path.home() / ".messagecipher" / "theme.json"
        else:
            self._config_path = Path(config_path)

        self._mode: str = self.load()

    def get_current_mode(self) -> str:
        """Return 'dark' or 'light'."""
        return self._mode

    def toggle(self) -> str:
        """Switch mode and persist. Returns new mode name."""
        self._mode = "light" if self._mode == "dark" else "dark"
        self.persist()
        return self._mode

    def get_scheme(self) -> dict[str, str]:
        """Return current color scheme dictionary."""
        if self._mode == "dark":
            return dict(self.DARK_SCHEME)
        return dict(self.LIGHT_SCHEME)

    def persist(self) -> None:
        """Write current mode to config file.

        If the config directory cannot be created or the file cannot be written,
        silently falls back to in-memory theme without persistence.
        """
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"mode": self._mode, "version": 1}
            self._config_path.write_text(
                json.dumps(data, indent=2), encoding="utf-8"
            )
        except OSError:
            # Config directory not writable — silently fall back to in-memory theme
            pass

    def load(self) -> str:
        """Load persisted mode from config, or detect system default.

        - If a valid config file exists, returns the stored mode.
        - If the config is corrupted or unreadable, deletes it and defaults to light.
        - If no config file exists (first launch), attempts to detect the system
          appearance mode. Falls back to 'light' if detection is not possible.

        Returns:
            'dark' or 'light'
        """
        if self._config_path.exists():
            try:
                content = self._config_path.read_text(encoding="utf-8")
                data = json.loads(content)
                mode = data.get("mode")
                if mode in ("dark", "light"):
                    return mode
                # Invalid mode value — treat as corrupted
                raise ValueError("Invalid mode value")
            except (json.JSONDecodeError, ValueError, KeyError, TypeError, OSError):
                # Corrupted config — delete and default to light
                try:
                    self._config_path.unlink()
                except OSError:
                    pass
                return "light"

        # No config file — first launch, try to detect system appearance
        return self._detect_system_appearance()

    def _detect_system_appearance(self) -> str:
        """Attempt to detect the system's dark/light appearance mode.

        Returns:
            'dark' if the system is using dark mode, 'light' otherwise or if
            detection fails.
        """
        system = platform.system()

        try:
            if system == "Windows":
                return self._detect_windows_appearance()
            elif system == "Darwin":
                return self._detect_macos_appearance()
            elif system == "Linux":
                return self._detect_linux_appearance()
        except Exception:
            pass

        return "light"

    def _detect_windows_appearance(self) -> str:
        """Detect dark mode on Windows via registry."""
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except Exception:
            return "light"

    def _detect_macos_appearance(self) -> str:
        """Detect dark mode on macOS via defaults command."""
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and "dark" in result.stdout.lower():
                return "dark"
        except Exception:
            pass
        return "light"

    def _detect_linux_appearance(self) -> str:
        """Detect dark mode on Linux via gsettings (GNOME) or similar."""
        try:
            result = subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.interface",
                    "color-scheme",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and "dark" in result.stdout.lower():
                return "dark"
        except Exception:
            pass
        return "light"
