"""Configuration management for CREST TUI."""

import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONFIG_DIR = Path.home() / ".config" / "crest-tui"
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class AppConfig:
    crest_binary: str = "crest"
    xtb_binary: str = "xtb"
    threads: int = 4
    scratch_dir: str = ""
    verbosity: int = 1
    default_method: str = "gfn2"
    theme: str = "dark"


def detect_binary(name: str) -> str:
    """Detect binary location using shutil.which."""
    found = shutil.which(name)
    return found if found is not None else name


def get_default_config() -> AppConfig:
    """Return AppConfig with auto-detected binaries."""
    return AppConfig(
        crest_binary=detect_binary("crest"),
        xtb_binary=detect_binary("xtb"),
        threads=4,
        scratch_dir="",
        verbosity=1,
        default_method="gfn2",
        theme="dark",
    )


def load_config() -> AppConfig:
    """Load config from ~/.config/crest-tui/config.toml."""
    if not CONFIG_FILE.exists():
        return get_default_config()
    try:
        with open(CONFIG_FILE, "rb") as fh:
            data = tomllib.load(fh)
        return AppConfig(
            crest_binary=data.get("crest_binary", "crest"),
            xtb_binary=data.get("xtb_binary", "xtb"),
            threads=int(data.get("threads", 4)),
            scratch_dir=data.get("scratch_dir", ""),
            verbosity=int(data.get("verbosity", 1)),
            default_method=data.get("default_method", "gfn2"),
            theme=data.get("theme", "dark"),
        )
    except Exception:
        return get_default_config()


def save_config(config: AppConfig) -> None:
    """Save config to ~/.config/crest-tui/config.toml."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "crest_binary": config.crest_binary,
        "xtb_binary": config.xtb_binary,
        "threads": config.threads,
        "scratch_dir": config.scratch_dir,
        "verbosity": config.verbosity,
        "default_method": config.default_method,
        "theme": config.theme,
    }
    with open(CONFIG_FILE, "wb") as fh:
        tomli_w.dump(data, fh)
