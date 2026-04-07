"""Tests for crest_tui.toml_builder."""

import pytest

from crest_tui.toml_builder import (
    CREGENParams,
    ConformerSearchParams,
    ConstrainedParams,
    DynamicsParams,
    EntropyParams,
    MSREACTParams,
    NCIParams,
    OptimizationParams,
    ProtonationParams,
    QCGParams,
    build_conformer_search_toml,
    build_constrained_toml,
    build_cregen_toml,
    build_dynamics_toml,
    build_entropy_toml,
    build_msreact_toml,
    build_nci_toml,
    build_optimization_toml,
    build_protonation_toml,
    build_qcg_toml,
    save_toml,
    toml_to_string,
)


# ── Basic output checks ──────────────────────────────────────────────────────

class TestConformerSearch:
    def test_returns_non_empty_dict(self):
        params = ConformerSearchParams(input_file="mol.xyz")
        result = build_conformer_search_toml(params)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_required_keys(self):
        params = ConformerSearchParams(input_file="mol.xyz", method="gfn2", charge=0, uhf=0)
        result = build_conformer_search_toml(params)
        assert "input" in result
        assert "runtype" in result
        assert "threads" in result
        assert "calculation" in result

    def test_runtype_is_imtd_gc(self):
        params = ConformerSearchParams()
        result = build_conformer_search_toml(params)
        assert result["runtype"] == "imtd-gc"

    def test_ewin_and_rthr(self):
        params = ConformerSearchParams(ewin=8.0, rthr=0.2)
        result = build_conformer_search_toml(params)
        assert result["ewin"] == 8.0
        assert result["rthr"] == 0.2

    def test_calculation_level_present(self):
        params = ConformerSearchParams(method="gfn1", charge=1, uhf=1)
        result = build_conformer_search_toml(params)
        level = result["calculation"]["level"][0]
        assert level["method"] == "gfn1"
        assert level["charge"] == 1
        assert level["uhf"] == 1

    def test_solvent_included_when_set(self):
        params = ConformerSearchParams(solvent="water")
        result = build_conformer_search_toml(params)
        level = result["calculation"]["level"][0]
        assert level.get("solvent") == "water"

    def test_no_solvent_key_when_empty(self):
        params = ConformerSearchParams(solvent="")
        result = build_conformer_search_toml(params)
        level = result["calculation"]["level"][0]
        assert "solvent" not in level


class TestEntropy:
    def test_returns_non_empty_dict(self):
        params = EntropyParams(input_file="mol.xyz")
        assert len(build_entropy_toml(params)) > 0

    def test_runtype(self):
        assert build_entropy_toml(EntropyParams())["runtype"] == "entropy"

    def test_trange_present(self):
        params = EntropyParams(trange=[200.0, 500.0, 25.0])
        result = build_entropy_toml(params)
        assert result["trange"] == [200.0, 500.0, 25.0]


class TestConstrained:
    def test_returns_non_empty_dict(self):
        params = ConstrainedParams(input_file="mol.xyz")
        assert len(build_constrained_toml(params)) > 0

    def test_required_keys(self):
        result = build_constrained_toml(ConstrainedParams())
        assert "runtype" in result
        assert "calculation" in result

    def test_constraints_added(self):
        params = ConstrainedParams(constraints=[{"type": "fix", "atoms": [1, 2]}])
        result = build_constrained_toml(params)
        assert result["calculation"]["constraints"] == [{"type": "fix", "atoms": [1, 2]}]


class TestProtonation:
    def test_protonate_runtype(self):
        params = ProtonationParams(mode="protonate")
        assert build_protonation_toml(params)["runtype"] == "protonate"

    def test_deprotonate_runtype(self):
        params = ProtonationParams(mode="deprotonate")
        assert build_protonation_toml(params)["runtype"] == "deprotonate"


class TestNCI:
    def test_runtype(self):
        assert build_nci_toml(NCIParams())["runtype"] == "nci"

    def test_ewin(self):
        params = NCIParams(ewin=10.0)
        assert build_nci_toml(params)["ewin"] == 10.0


class TestQCG:
    def test_runtype(self):
        assert build_qcg_toml(QCGParams())["runtype"] == "qcg"

    def test_qcg_block(self):
        params = QCGParams(solvent_file="water.xyz", nsolv=10)
        result = build_qcg_toml(params)
        assert result["qcg"]["nsolv"] == 10
        assert result["qcg"]["solvent"] == "water.xyz"


class TestMSREACT:
    def test_runtype(self):
        assert build_msreact_toml(MSREACTParams())["runtype"] == "msreact"

    def test_msreact_block(self):
        params = MSREACTParams(react_temp=6000.0, nfrag=3)
        result = build_msreact_toml(params)
        assert result["msreact"]["react_temp"] == 6000.0
        assert result["msreact"]["nfrag"] == 3


class TestOptimization:
    def test_runtype(self):
        assert build_optimization_toml(OptimizationParams())["runtype"] == "optimize"

    def test_optlevel(self):
        params = OptimizationParams(optlevel="tight")
        assert build_optimization_toml(params)["optlevel"] == "tight"


class TestDynamics:
    def test_runtype(self):
        assert build_dynamics_toml(DynamicsParams())["runtype"] == "dynamics"

    def test_dynamics_block(self):
        params = DynamicsParams(time=100.0, tstep=2.0)
        result = build_dynamics_toml(params)
        assert result["dynamics"]["time"] == 100.0
        assert result["dynamics"]["tstep"] == 2.0


class TestCREGEN:
    def test_runtype(self):
        assert build_cregen_toml(CREGENParams())["runtype"] == "cregen"

    def test_thresholds(self):
        params = CREGENParams(ewin=5.0, rthr=0.1, ethr=0.02)
        result = build_cregen_toml(params)
        assert result["ewin"] == 5.0
        assert result["rthr"] == 0.1
        assert result["ethr"] == 0.02


# ── TOML serialization ────────────────────────────────────────────────────────

class TestTomlSerialization:
    def test_toml_to_string_non_empty(self):
        params = ConformerSearchParams(input_file="mol.xyz")
        data = build_conformer_search_toml(params)
        text = toml_to_string(data)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_toml_to_string_contains_runtype(self):
        data = build_conformer_search_toml(ConformerSearchParams())
        text = toml_to_string(data)
        assert "imtd-gc" in text

    def test_save_toml(self, tmp_path):
        params = ConformerSearchParams(input_file="mol.xyz")
        data = build_conformer_search_toml(params)
        out = tmp_path / "test.toml"
        save_toml(data, out)
        assert out.exists()
        assert out.stat().st_size > 0
