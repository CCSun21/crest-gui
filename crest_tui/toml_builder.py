"""TOML builder for CREST 3.0 input files."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


# ── Parameter dataclasses ────────────────────────────────────────────────────

@dataclass
class ConformerSearchParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    solvent: str = ""
    ewin: float = 6.0
    rthr: float = 0.125
    temperature: float = 298.15
    threads: int = 4
    extra_flags: str = ""


@dataclass
class EntropyParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    temperature: float = 298.15
    trange: list = field(default_factory=lambda: [200.0, 400.0, 10.0])
    threads: int = 4
    extra_flags: str = ""


@dataclass
class ConstrainedParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    ewin: float = 6.0
    rthr: float = 0.125
    threads: int = 4
    constraints: list = field(default_factory=list)
    extra_flags: str = ""


@dataclass
class ProtonationParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    solvent: str = ""
    threads: int = 4
    mode: str = "protonate"
    extra_flags: str = ""


@dataclass
class NCIParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    threads: int = 4
    ewin: float = 6.0
    extra_flags: str = ""


@dataclass
class QCGParams:
    input_file: str = ""
    solvent_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    nsolv: int = 5
    threads: int = 4
    ensemble: bool = False
    extra_flags: str = ""


@dataclass
class MSREACTParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    threads: int = 4
    react_temp: float = 5000.0
    nfrag: int = 2
    extra_flags: str = ""


@dataclass
class OptimizationParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    optlevel: str = "normal"
    threads: int = 4
    extra_flags: str = ""


@dataclass
class DynamicsParams:
    input_file: str = ""
    method: str = "gfn2"
    charge: int = 0
    uhf: int = 0
    time: float = 50.0
    tstep: float = 5.0
    temperature: float = 298.15
    shake: int = 2
    dump: int = 250
    threads: int = 4
    extra_flags: str = ""


@dataclass
class CREGENParams:
    input_file: str = ""
    ewin: float = 6.0
    rthr: float = 0.125
    ethr: float = 0.05
    method: str = "gfn2"
    threads: int = 4
    extra_flags: str = ""


# ── Builder functions ─────────────────────────────────────────────────────────

def _base_calculation_block(method: str, charge: int, uhf: int, solvent: str = "") -> dict:
    level: dict[str, Any] = {"method": method, "charge": charge, "uhf": uhf}
    if solvent:
        level["solvent"] = solvent
    return {"level": [level]}


def build_conformer_search_toml(params: ConformerSearchParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "imtd-gc",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf, params.solvent),
    }
    data["ewin"] = params.ewin
    data["rthr"] = params.rthr
    data["temperature"] = params.temperature
    return data


def build_entropy_toml(params: EntropyParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "entropy",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf),
        "temperature": params.temperature,
        "trange": params.trange,
    }
    return data


def build_constrained_toml(params: ConstrainedParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "imtd-gc",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf),
        "ewin": params.ewin,
        "rthr": params.rthr,
    }
    if params.constraints:
        data["calculation"]["constraints"] = params.constraints
    return data


def build_protonation_toml(params: ProtonationParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": params.mode,
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf, params.solvent),
    }
    return data


def build_nci_toml(params: NCIParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "nci",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf),
        "ewin": params.ewin,
    }
    return data


def build_qcg_toml(params: QCGParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "qcg",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf),
        "qcg": {
            "solvent": params.solvent_file,
            "nsolv": params.nsolv,
            "ensemble": params.ensemble,
        },
    }
    return data


def build_msreact_toml(params: MSREACTParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "msreact",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf),
        "msreact": {
            "react_temp": params.react_temp,
            "nfrag": params.nfrag,
        },
    }
    return data


def build_optimization_toml(params: OptimizationParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "optimize",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf),
        "optlevel": params.optlevel,
    }
    return data


def build_dynamics_toml(params: DynamicsParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "dynamics",
        "threads": params.threads,
        "calculation": _base_calculation_block(params.method, params.charge, params.uhf),
        "dynamics": {
            "time": params.time,
            "tstep": params.tstep,
            "temperature": params.temperature,
            "shake": params.shake,
            "dump": params.dump,
        },
    }
    return data


def build_cregen_toml(params: CREGENParams) -> dict:
    data: dict[str, Any] = {
        "input": params.input_file,
        "runtype": "cregen",
        "threads": params.threads,
        "ewin": params.ewin,
        "rthr": params.rthr,
        "ethr": params.ethr,
    }
    return data


def toml_to_string(data: dict) -> str:
    """Serialize dict to TOML string using tomli_w."""
    return tomli_w.dumps(data)


def save_toml(data: dict, path: str | Path) -> None:
    """Write TOML dict to file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        tomli_w.dump(data, fh)
