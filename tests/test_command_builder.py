"""Tests for crest_tui.command_builder."""

import pytest

from crest_tui.command_builder import (
    build_command,
    build_legacy_command,
    preview_command,
)
from crest_tui.config import AppConfig


class TestBuildCommand:
    def _config(self) -> AppConfig:
        return AppConfig(crest_binary="crest", threads=4)

    def test_basic_command(self):
        config = self._config()
        cmd = build_command("mol.xyz", "input.toml", config)
        assert cmd[0] == "crest"
        assert "mol.xyz" in cmd
        assert "--input" in cmd
        assert "input.toml" in cmd

    def test_threads_in_command(self):
        config = AppConfig(crest_binary="crest", threads=8)
        cmd = build_command("mol.xyz", "input.toml", config)
        idx = cmd.index("--T")
        assert cmd[idx + 1] == "8"

    def test_dry_run_flag(self):
        config = self._config()
        cmd = build_command("mol.xyz", "input.toml", config, dry_run=True)
        assert "--dry" in cmd

    def test_no_dry_run_by_default(self):
        config = self._config()
        cmd = build_command("mol.xyz", "input.toml", config)
        assert "--dry" not in cmd

    def test_extra_flags(self):
        config = self._config()
        cmd = build_command("mol.xyz", "input.toml", config, extra_flags=["--quick"])
        assert "--quick" in cmd

    def test_returns_list(self):
        config = self._config()
        cmd = build_command("mol.xyz", "input.toml", config)
        assert isinstance(cmd, list)


class TestBuildLegacyCommand:
    def test_basic_legacy_command(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", crest_binary="crest")
        assert cmd[0] == "crest"
        assert "mol.xyz" in cmd

    def test_gfn2_flag(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", method="gfn2")
        assert "--gfn2" in cmd

    def test_gfn1_flag(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", method="gfn1")
        assert "--gfn1" in cmd

    def test_gfnff_flag(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", method="gfnff")
        assert "--gfnff" in cmd

    def test_entropy_runtype(self):
        cmd = build_legacy_command("mol.xyz", "entropy")
        assert "--entropy" in cmd

    def test_nci_runtype(self):
        cmd = build_legacy_command("mol.xyz", "nci")
        assert "--nci" in cmd

    def test_protonate_runtype(self):
        cmd = build_legacy_command("mol.xyz", "protonate")
        assert "--protonate" in cmd

    def test_deprotonate_runtype(self):
        cmd = build_legacy_command("mol.xyz", "deprotonate")
        assert "--deprotonate" in cmd

    def test_charge_nonzero(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", charge=2)
        assert "--chrg" in cmd
        idx = cmd.index("--chrg")
        assert cmd[idx + 1] == "2"

    def test_charge_zero_omitted(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", charge=0)
        assert "--chrg" not in cmd

    def test_uhf_nonzero(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", uhf=1)
        assert "--uhf" in cmd
        idx = cmd.index("--uhf")
        assert cmd[idx + 1] == "1"

    def test_uhf_zero_omitted(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", uhf=0)
        assert "--uhf" not in cmd

    def test_threads(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", threads=16)
        idx = cmd.index("--T")
        assert cmd[idx + 1] == "16"

    def test_dry_run(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", dry_run=True)
        assert "--dry" in cmd

    def test_extra_flags_list(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc", extra_flags=["--quick", "--norotmd"])
        assert "--quick" in cmd
        assert "--norotmd" in cmd

    def test_returns_list(self):
        cmd = build_legacy_command("mol.xyz", "imtd-gc")
        assert isinstance(cmd, list)
        assert all(isinstance(x, str) for x in cmd)


class TestPreviewCommand:
    def test_joins_with_space(self):
        cmd = ["crest", "mol.xyz", "--gfn2", "--T", "4"]
        result = preview_command(cmd)
        assert result == "crest mol.xyz --gfn2 --T 4"

    def test_returns_string(self):
        assert isinstance(preview_command(["crest"]), str)

    def test_empty_list(self):
        assert preview_command([]) == ""
