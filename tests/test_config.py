"""Tests for crest_tui.config."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from crest_tui.config import (
    AppConfig,
    detect_binary,
    get_default_config,
    load_config,
    save_config,
)


class TestAppConfig:
    def test_default_values(self):
        config = AppConfig()
        assert config.crest_binary == "crest"
        assert config.xtb_binary == "xtb"
        assert config.threads == 4
        assert config.scratch_dir == ""
        assert config.verbosity == 1
        assert config.default_method == "gfn2"
        assert config.theme == "dark"

    def test_custom_values(self):
        config = AppConfig(crest_binary="/usr/local/bin/crest", threads=16)
        assert config.crest_binary == "/usr/local/bin/crest"
        assert config.threads == 16


class TestDetectBinary:
    def test_found_binary(self):
        with patch("shutil.which", return_value="/usr/bin/crest"):
            result = detect_binary("crest")
        assert result == "/usr/bin/crest"

    def test_not_found_returns_name(self):
        with patch("shutil.which", return_value=None):
            result = detect_binary("crest")
        assert result == "crest"

    def test_calls_which_with_name(self):
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/path/to/xtb"
            detect_binary("xtb")
            mock_which.assert_called_once_with("xtb")


class TestGetDefaultConfig:
    def test_returns_app_config(self):
        config = get_default_config()
        assert isinstance(config, AppConfig)

    def test_default_threads(self):
        config = get_default_config()
        assert config.threads == 4

    def test_uses_detected_binaries(self):
        with patch("crest_tui.config.detect_binary") as mock_detect:
            mock_detect.side_effect = lambda name: f"/fake/{name}"
            config = get_default_config()
        assert config.crest_binary == "/fake/crest"
        assert config.xtb_binary == "/fake/xtb"


class TestSaveAndLoadConfig:
    def test_round_trip(self, tmp_path):
        config = AppConfig(
            crest_binary="/bin/crest",
            xtb_binary="/bin/xtb",
            threads=8,
            scratch_dir="/scratch",
            verbosity=2,
            default_method="gfn1",
            theme="light",
        )
        config_file = tmp_path / "config.toml"
        with patch("crest_tui.config.CONFIG_FILE", config_file), \
             patch("crest_tui.config.CONFIG_DIR", tmp_path):
            save_config(config)
            assert config_file.exists()
            loaded = load_config()

        assert loaded.crest_binary == "/bin/crest"
        assert loaded.xtb_binary == "/bin/xtb"
        assert loaded.threads == 8
        assert loaded.scratch_dir == "/scratch"
        assert loaded.verbosity == 2
        assert loaded.default_method == "gfn1"
        assert loaded.theme == "light"

    def test_save_creates_directory(self, tmp_path):
        config_dir = tmp_path / "subdir" / "crest-tui"
        config_file = config_dir / "config.toml"
        config = AppConfig()
        with patch("crest_tui.config.CONFIG_FILE", config_file), \
             patch("crest_tui.config.CONFIG_DIR", config_dir):
            save_config(config)
        assert config_file.exists()

    def test_load_missing_file_returns_defaults(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.toml"
        with patch("crest_tui.config.CONFIG_FILE", nonexistent):
            config = load_config()
        assert isinstance(config, AppConfig)
        assert config.threads == 4

    def test_load_corrupt_file_returns_defaults(self, tmp_path):
        bad_file = tmp_path / "bad.toml"
        bad_file.write_text("this is not valid toml [[[")
        with patch("crest_tui.config.CONFIG_FILE", bad_file):
            config = load_config()
        assert isinstance(config, AppConfig)

    def test_saved_file_is_toml(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config = AppConfig(crest_binary="mycrest")
        with patch("crest_tui.config.CONFIG_FILE", config_file), \
             patch("crest_tui.config.CONFIG_DIR", tmp_path):
            save_config(config)
        content = config_file.read_text()
        assert "mycrest" in content
        assert "crest_binary" in content
