"""Tests for crest_tui.parser."""

import math
from pathlib import Path

import pytest

from crest_tui.parser import (
    calculate_boltzmann_populations,
    format_molecular_formula,
    parse_energy_log,
    parse_stdout,
    parse_xyz_ensemble,
)

# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_STDOUT = """
 CREST iMTD-GC sampling
 Number of unique conformers for further ensemble steps: 42
 Lowest energy conformer has energy: -500.123456 Eh
 CREST wall time 0h 5m 23.4s
 WARNING: some convergence issue
 NORMAL TERMINATION
"""

SAMPLE_XYZ = """\
5
Energy: -500.123456
C  0.000000  0.000000  0.000000
H  0.629118  0.629118  0.629118
H -0.629118 -0.629118  0.629118
H -0.629118  0.629118 -0.629118
H  0.629118 -0.629118 -0.629118
5
Energy: -500.120000
C  0.010000  0.010000  0.010000
H  0.639118  0.639118  0.639118
H -0.619118 -0.619118  0.639118
H -0.619118  0.639118 -0.619118
H  0.639118 -0.619118 -0.619118
"""

SAMPLE_ENERGY_LOG = """\
# energy log
-500.123456
-500.120000
-500.115000
"""


# ── parse_stdout ──────────────────────────────────────────────────────────────

class TestParseStdout:
    def test_returns_dict(self):
        result = parse_stdout(SAMPLE_STDOUT)
        assert isinstance(result, dict)

    def test_n_conformers(self):
        result = parse_stdout(SAMPLE_STDOUT)
        assert result["n_conformers"] == 42

    def test_lowest_energy(self):
        result = parse_stdout(SAMPLE_STDOUT)
        assert result["lowest_energy"] == pytest.approx(-500.123456)

    def test_wall_time(self):
        result = parse_stdout(SAMPLE_STDOUT)
        assert result["wall_time"] is not None
        assert "5m" in result["wall_time"] or "5" in result["wall_time"]

    def test_warnings_captured(self):
        result = parse_stdout(SAMPLE_STDOUT)
        assert len(result["warnings"]) >= 1
        assert any("convergence" in w.lower() for w in result["warnings"])

    def test_empty_text(self):
        result = parse_stdout("")
        assert result["n_conformers"] is None
        assert result["lowest_energy"] is None
        assert result["warnings"] == []

    def test_keys_present(self):
        result = parse_stdout(SAMPLE_STDOUT)
        for key in ("n_conformers", "lowest_energy", "wall_time", "warnings"):
            assert key in result


# ── parse_xyz_ensemble ────────────────────────────────────────────────────────

class TestParseXyzEnsemble:
    def test_returns_list(self, tmp_path):
        xyz_file = tmp_path / "ensemble.xyz"
        xyz_file.write_text(SAMPLE_XYZ)
        result = parse_xyz_ensemble(xyz_file)
        assert isinstance(result, list)

    def test_correct_number_of_conformers(self, tmp_path):
        xyz_file = tmp_path / "ensemble.xyz"
        xyz_file.write_text(SAMPLE_XYZ)
        result = parse_xyz_ensemble(xyz_file)
        assert len(result) == 2

    def test_conformer_keys(self, tmp_path):
        xyz_file = tmp_path / "ensemble.xyz"
        xyz_file.write_text(SAMPLE_XYZ)
        conf = parse_xyz_ensemble(xyz_file)[0]
        for key in ("index", "energy", "coords", "formula"):
            assert key in conf

    def test_energy_parsed(self, tmp_path):
        xyz_file = tmp_path / "ensemble.xyz"
        xyz_file.write_text(SAMPLE_XYZ)
        conf = parse_xyz_ensemble(xyz_file)[0]
        assert conf["energy"] == pytest.approx(-500.123456)

    def test_formula_parsed(self, tmp_path):
        xyz_file = tmp_path / "ensemble.xyz"
        xyz_file.write_text(SAMPLE_XYZ)
        conf = parse_xyz_ensemble(xyz_file)[0]
        assert conf["formula"] == "CH4"

    def test_coords_count(self, tmp_path):
        xyz_file = tmp_path / "ensemble.xyz"
        xyz_file.write_text(SAMPLE_XYZ)
        conf = parse_xyz_ensemble(xyz_file)[0]
        assert len(conf["coords"]) == 5

    def test_index_increments(self, tmp_path):
        xyz_file = tmp_path / "ensemble.xyz"
        xyz_file.write_text(SAMPLE_XYZ)
        result = parse_xyz_ensemble(xyz_file)
        assert result[0]["index"] == 0
        assert result[1]["index"] == 1

    def test_empty_file(self, tmp_path):
        xyz_file = tmp_path / "empty.xyz"
        xyz_file.write_text("")
        result = parse_xyz_ensemble(xyz_file)
        assert result == []


# ── parse_energy_log ──────────────────────────────────────────────────────────

class TestParseEnergyLog:
    def test_returns_list(self, tmp_path):
        f = tmp_path / "energies.log"
        f.write_text(SAMPLE_ENERGY_LOG)
        result = parse_energy_log(f)
        assert isinstance(result, list)

    def test_correct_values(self, tmp_path):
        f = tmp_path / "energies.log"
        f.write_text(SAMPLE_ENERGY_LOG)
        result = parse_energy_log(f)
        assert len(result) == 3
        assert result[0] == pytest.approx(-500.123456)

    def test_skips_comments(self, tmp_path):
        f = tmp_path / "energies.log"
        f.write_text(SAMPLE_ENERGY_LOG)
        result = parse_energy_log(f)
        # comment line should not appear as a float
        assert all(isinstance(v, float) for v in result)


# ── calculate_boltzmann_populations ──────────────────────────────────────────

class TestBoltzmannPopulations:
    def test_returns_list(self):
        result = calculate_boltzmann_populations([0.0, 1.0, 2.0])
        assert isinstance(result, list)

    def test_sums_to_one(self):
        energies = [0.0, 0.5, 1.0, 2.0, 5.0]
        pops = calculate_boltzmann_populations(energies, temperature=298.15)
        assert sum(pops) == pytest.approx(1.0, abs=1e-9)

    def test_lowest_energy_highest_population(self):
        energies = [0.0, 1.0, 5.0]
        pops = calculate_boltzmann_populations(energies)
        assert pops[0] > pops[1] > pops[2]

    def test_equal_energies_equal_populations(self):
        energies = [5.0, 5.0, 5.0]
        pops = calculate_boltzmann_populations(energies)
        assert pops[0] == pytest.approx(1 / 3)
        assert pops[1] == pytest.approx(1 / 3)

    def test_single_energy(self):
        pops = calculate_boltzmann_populations([0.0])
        assert pops == [pytest.approx(1.0)]

    def test_empty_returns_empty(self):
        assert calculate_boltzmann_populations([]) == []

    def test_all_non_negative(self):
        energies = [0.0, 0.2, 0.8, 3.5]
        pops = calculate_boltzmann_populations(energies)
        assert all(p >= 0.0 for p in pops)

    def test_high_temperature_more_uniform(self):
        energies = [0.0, 1.0]
        pops_low = calculate_boltzmann_populations(energies, temperature=10.0)
        pops_high = calculate_boltzmann_populations(energies, temperature=10000.0)
        diff_low = abs(pops_low[0] - pops_low[1])
        diff_high = abs(pops_high[0] - pops_high[1])
        assert diff_high < diff_low


# ── format_molecular_formula ──────────────────────────────────────────────────

class TestFormatMolecularFormula:
    def test_methane(self):
        assert format_molecular_formula(["C", "H", "H", "H", "H"]) == "CH4"

    def test_ethanol(self):
        atoms = ["C", "C", "H", "H", "H", "H", "H", "O", "H"]
        result = format_molecular_formula(atoms)
        assert result.startswith("C2")
        assert "O" in result

    def test_water(self):
        assert format_molecular_formula(["H", "O", "H"]) == "H2O"

    def test_single_carbon(self):
        result = format_molecular_formula(["C"])
        assert result == "C"

    def test_empty_list(self):
        assert format_molecular_formula([]) == ""

    def test_c_before_h_before_others(self):
        atoms = ["N", "H", "H", "H", "C"]
        result = format_molecular_formula(atoms)
        # Hill order: C first, then H, then N
        c_pos = result.find("C")
        h_pos = result.find("H")
        n_pos = result.find("N")
        assert c_pos < h_pos < n_pos

    def test_no_c_alphabetical(self):
        atoms = ["N", "O", "H", "H"]
        result = format_molecular_formula(atoms)
        assert result.startswith("H")
