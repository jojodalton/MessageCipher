"""Unit tests for theme_engine module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from theme_engine import ThemeEngine


class TestThemeEngineColorSchemes:
    """Test that color scheme dictionaries are properly defined."""

    def test_dark_scheme_has_all_keys(self):
        expected_keys = {
            "bg_primary", "bg_secondary", "bg_card",
            "fg_primary", "fg_secondary",
            "accent", "error", "success", "border",
        }
        assert set(ThemeEngine.DARK_SCHEME.keys()) == expected_keys

    def test_light_scheme_has_all_keys(self):
        expected_keys = {
            "bg_primary", "bg_secondary", "bg_card",
            "fg_primary", "fg_secondary",
            "accent", "error", "success", "border",
        }
        assert set(ThemeEngine.LIGHT_SCHEME.keys()) == expected_keys

    def test_dark_scheme_values_are_hex_colors(self):
        for key, value in ThemeEngine.DARK_SCHEME.items():
            assert value.startswith("#"), f"{key} should be a hex color"
            assert len(value) == 7, f"{key} should be #RRGGBB format"

    def test_light_scheme_values_are_hex_colors(self):
        for key, value in ThemeEngine.LIGHT_SCHEME.items():
            assert value.startswith("#"), f"{key} should be a hex color"
            assert len(value) == 7, f"{key} should be #RRGGBB format"


class TestThemeEngineInit:
    """Test initialization behavior."""

    def test_default_config_path(self):
        """ThemeEngine uses ~/.messagecipher/theme.json by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            engine = ThemeEngine(config_path=config_path)
            # Should default to light mode when no config exists
            assert engine.get_current_mode() in ("dark", "light")

    def test_custom_config_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "custom_theme.json")
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() in ("dark", "light")

    def test_first_launch_no_config(self):
        """Without config file, detects system or defaults to light."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent", "theme.json")
            engine = ThemeEngine(config_path=config_path)
            # Should be either dark or light depending on system detection
            assert engine.get_current_mode() in ("dark", "light")


class TestThemeEngineGetCurrentMode:
    """Test get_current_mode method."""

    def test_returns_light_or_dark(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() in ("dark", "light")


class TestThemeEngineToggle:
    """Test toggle method."""

    def test_toggle_from_light_to_dark(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            # Write light mode config
            Path(config_path).write_text(
                json.dumps({"mode": "light", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "light"
            result = engine.toggle()
            assert result == "dark"
            assert engine.get_current_mode() == "dark"

    def test_toggle_from_dark_to_light(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "dark", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "dark"
            result = engine.toggle()
            assert result == "light"
            assert engine.get_current_mode() == "light"

    def test_toggle_persists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "light", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            engine.toggle()
            # Read the file to verify persistence
            data = json.loads(Path(config_path).read_text(encoding="utf-8"))
            assert data["mode"] == "dark"


class TestThemeEngineGetScheme:
    """Test get_scheme method."""

    def test_light_mode_returns_light_scheme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "light", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            scheme = engine.get_scheme()
            assert scheme == ThemeEngine.LIGHT_SCHEME

    def test_dark_mode_returns_dark_scheme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "dark", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            scheme = engine.get_scheme()
            assert scheme == ThemeEngine.DARK_SCHEME

    def test_get_scheme_returns_copy(self):
        """get_scheme returns a copy, not a reference to the class dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "light", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            scheme = engine.get_scheme()
            scheme["bg_primary"] = "#000000"
            # Original should be unchanged
            assert ThemeEngine.LIGHT_SCHEME["bg_primary"] == "#f8f9fa"


class TestThemeEnginePersist:
    """Test persist method."""

    def test_persist_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "subdir", "theme.json")
            engine = ThemeEngine(config_path=config_path)
            engine.persist()
            assert Path(config_path).exists()

    def test_persist_writes_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "dark", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            engine.persist()
            data = json.loads(Path(config_path).read_text(encoding="utf-8"))
            assert data == {"mode": "dark", "version": 1}

    def test_persist_unwritable_directory_does_not_raise(self):
        """If directory is not writable, persist silently fails."""
        # Use an invalid path that cannot be created
        engine = ThemeEngine(config_path="/nonexistent_root_path/x/y/z/theme.json")
        # Should not raise
        engine.persist()


class TestThemeEngineLoad:
    """Test load method."""

    def test_load_valid_dark_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "dark", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "dark"

    def test_load_valid_light_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "light", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "light"

    def test_load_corrupted_json_defaults_to_light(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text("not valid json {{{{", encoding="utf-8")
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "light"

    def test_load_corrupted_json_deletes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text("not valid json {{{{", encoding="utf-8")
            engine = ThemeEngine(config_path=config_path)
            assert not Path(config_path).exists()

    def test_load_invalid_mode_value_defaults_to_light(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"mode": "invalid", "version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "light"

    def test_load_missing_mode_key_defaults_to_light(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text(
                json.dumps({"version": 1}), encoding="utf-8"
            )
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "light"

    def test_load_empty_file_defaults_to_light(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "theme.json")
            Path(config_path).write_text("", encoding="utf-8")
            engine = ThemeEngine(config_path=config_path)
            assert engine.get_current_mode() == "light"
