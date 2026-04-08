"""Command builder for CREST CLI invocations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from crest_tui.config import AppConfig


def build_command(
    struct_file: str,
    toml_file: str,
    config: AppConfig,
    extra_flags: list[str] | None = None,
    dry_run: bool = False,
) -> list[str]:
    """Build a CREST 3.0 command using a TOML input file."""
    cmd = [config.crest_binary, struct_file, "--input", toml_file, "--T", str(config.threads)]
    if dry_run:
        cmd.append("--dry")
    if extra_flags:
        cmd.extend(extra_flags)
    return cmd


def build_legacy_command(
    struct_file: str,
    runtype: str,
    method: str = "gfn2",
    charge: int = 0,
    uhf: int = 0,
    threads: int = 4,
    extra_flags: list[str] | None = None,
    dry_run: bool = False,
    crest_binary: str = "crest",
) -> list[str]:
    """Build a legacy (pre-3.0) CREST command using CLI flags."""
    cmd = [crest_binary, struct_file]

    runtype_flags: dict[str, list[str]] = {
        "imtd-gc": [],
        "entropy": ["--entropy"],
        "nci": ["--nci"],
        "protonate": ["--protonate"],
        "deprotonate": ["--deprotonate"],
        "tautomerize": ["--tautomerize"],
        "qcg": ["--qcg"],
        "msreact": ["--msreact"],
        "optimize": ["--opt"],
        "cregen": ["--cregen"],
    }
    cmd.extend(runtype_flags.get(runtype, []))

    method_map = {
        "gfn2": ["--gfn2"],
        "gfn1": ["--gfn1"],
        "gfn0": ["--gfn0"],
        "gfnff": ["--gfnff"],
    }
    cmd.extend(method_map.get(method, ["--gfn2"]))

    if charge != 0:
        cmd += ["--chrg", str(charge)]
    if uhf != 0:
        cmd += ["--uhf", str(uhf)]

    cmd += ["--T", str(threads)]

    if dry_run:
        cmd.append("--dry")

    if extra_flags:
        cmd.extend(extra_flags)

    return cmd


def preview_command(cmd: list[str]) -> str:
    """Return human-readable command string."""
    return " ".join(cmd)
