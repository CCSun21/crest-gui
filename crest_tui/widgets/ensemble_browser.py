"""Ensemble browser widget."""

from pathlib import Path

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Static

from crest_tui.parser import calculate_boltzmann_populations, parse_xyz_ensemble

KCAL_PER_EH = 627.5094740631


class EnsembleBrowser(Widget):
    """Displays a multi-XYZ ensemble with relative energies and populations."""

    filepath: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Static(id="ensemble-info", markup=True)
        yield DataTable(id="ensemble-table")

    def on_mount(self) -> None:
        table = self.query_one("#ensemble-table", DataTable)
        table.add_columns("#", "Formula", "Energy (Eh)", "ΔE (kcal/mol)", "Pop. (%)")

    def watch_filepath(self, path: str) -> None:
        self._load_file(path)

    def load(self, path: str | Path) -> None:
        self.filepath = str(path)

    def _load_file(self, path: str) -> None:
        if not path:
            return
        try:
            conformers = parse_xyz_ensemble(path)
            if not conformers:
                self.query_one("#ensemble-info", Static).update("[red]No conformers found.[/red]")
                return

            energies_eh = [c["energy"] for c in conformers if c["energy"] is not None]
            pops: list[float] = []
            if energies_eh:
                energies_kcal = [e * KCAL_PER_EH for e in energies_eh]
                pops = calculate_boltzmann_populations(energies_kcal)

            min_e = min(energies_eh) if energies_eh else 0.0
            self.query_one("#ensemble-info", Static).update(
                f"[bold]Conformers:[/bold] {len(conformers)}  [bold]File:[/bold] {path}"
            )
            table = self.query_one("#ensemble-table", DataTable)
            table.clear()
            pop_idx = 0
            for conf in conformers:
                e = conf["energy"]
                if e is not None:
                    de = (e - min_e) * KCAL_PER_EH
                    pop_pct = pops[pop_idx] * 100.0 if pop_idx < len(pops) else 0.0
                    pop_idx += 1
                    table.add_row(
                        str(conf["index"] + 1),
                        conf["formula"],
                        f"{e:.6f}",
                        f"{de:.2f}",
                        f"{pop_pct:.1f}",
                    )
                else:
                    table.add_row(str(conf["index"] + 1), conf["formula"], "N/A", "N/A", "N/A")
        except (FileNotFoundError, OSError, ValueError) as exc:
            self.query_one("#ensemble-info", Static).update(f"[red]Error: {exc}[/red]")
