"""Parsers for CREST output files and stdout."""

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


def parse_stdout(text: str) -> dict[str, Any]:
    """Parse CREST stdout and extract summary information."""
    result: dict[str, Any] = {
        "n_conformers": None,
        "lowest_energy": None,
        "wall_time": None,
        "warnings": [],
    }

    # Number of conformers
    m = re.search(r"(\d+)\s+conformers?\s+written", text, re.IGNORECASE)
    if m:
        result["n_conformers"] = int(m.group(1))

    m2 = re.search(r"number of unique conformers.*?:\s*(\d+)", text, re.IGNORECASE)
    if m2:
        result["n_conformers"] = int(m2.group(1))

    # Lowest energy (Eh)
    m3 = re.search(r"lowest\s+energy.*?(-\d+\.\d+)", text, re.IGNORECASE)
    if m3:
        result["lowest_energy"] = float(m3.group(1))

    # Wall time
    m4 = re.search(r"CREST\s+wall\s+time.*?(\d+h\s*\d+m\s*\d+\.\d+s|\d+\.\d+\s*seconds?)", text, re.IGNORECASE)
    if m4:
        result["wall_time"] = m4.group(1).strip()

    # Warnings
    for line in text.splitlines():
        if "WARNING" in line.upper() or "ERROR" in line.upper():
            result["warnings"].append(line.strip())

    return result


def parse_xyz_ensemble(path: str | Path) -> list[dict[str, Any]]:
    """Parse a multi-structure XYZ file into a list of conformer dicts."""
    path = Path(path)
    conformers: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    idx = 0
    conf_index = 0

    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue
        try:
            n_atoms = int(line)
        except ValueError:
            idx += 1
            continue

        comment = lines[idx + 1].strip() if idx + 1 < len(lines) else ""

        # Try to extract energy from comment line
        energy = None
        m = re.search(r"(-?\d+\.\d+)", comment)
        if m:
            energy = float(m.group(1))

        coords = []
        atoms = []
        for i in range(n_atoms):
            atom_line_idx = idx + 2 + i
            if atom_line_idx >= len(lines):
                break
            parts = lines[atom_line_idx].split()
            if len(parts) >= 4:
                element = parts[0]
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                atoms.append(element)
                coords.append((element, x, y, z))

        formula = format_molecular_formula(atoms)
        conformers.append({
            "index": conf_index,
            "energy": energy,
            "coords": coords,
            "formula": formula,
            "comment": comment,
        })
        conf_index += 1
        idx += 2 + n_atoms

    return conformers


def parse_energy_log(path: str | Path) -> list[float]:
    """Parse a file containing one energy per line (Eh)."""
    path = Path(path)
    energies = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parts = line.split()
            energies.append(float(parts[-1]))
        except (ValueError, IndexError):
            continue
    return energies


def calculate_boltzmann_populations(energies: list[float], temperature: float = 298.15) -> list[float]:
    """Calculate Boltzmann populations from energies in kcal/mol."""
    if not energies:
        return []
    R = 0.001987204  # kcal/(mol·K)
    kT = R * temperature
    min_e = min(energies)
    weights = [math.exp(-(e - min_e) / kT) for e in energies]
    total = sum(weights)
    if total == 0.0:
        n = len(energies)
        return [1.0 / n] * n
    return [w / total for w in weights]


def format_molecular_formula(atoms: list[str]) -> str:
    """Format list of element symbols into Hill-order molecular formula."""
    counter = Counter(atoms)
    parts = []
    # Carbon first, then hydrogen, then alphabetical
    for elem in ["C", "H"]:
        if elem in counter:
            count = counter.pop(elem)
            parts.append(elem if count == 1 else f"{elem}{count}")
    for elem in sorted(counter.keys()):
        count = counter[elem]
        parts.append(elem if count == 1 else f"{elem}{count}")
    return "".join(parts)
