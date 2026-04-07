"""XYZ structure viewer widget."""

from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label, Static

from crest_tui.parser import format_molecular_formula, parse_xyz_ensemble


class StructureViewer(Widget):
    """Displays an XYZ file in a DataTable with formula and atom count."""

    filepath: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Static(id="structure-info", markup=True)
        yield DataTable(id="atom-table")

    def on_mount(self) -> None:
        table = self.query_one("#atom-table", DataTable)
        table.add_columns("#", "Element", "X (Å)", "Y (Å)", "Z (Å)")

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
                self.query_one("#structure-info", Static).update("[red]No structures found.[/red]")
                return
            first = conformers[0]
            coords = first["coords"]
            atoms = [c[0] for c in coords]
            formula = format_molecular_formula(atoms)
            info = f"[bold]File:[/bold] {path}  [bold]Formula:[/bold] {formula}  [bold]Atoms:[/bold] {len(atoms)}"
            self.query_one("#structure-info", Static).update(info)
            table = self.query_one("#atom-table", DataTable)
            table.clear()
            for i, (elem, x, y, z) in enumerate(coords, start=1):
                table.add_row(str(i), elem, f"{x:.6f}", f"{y:.6f}", f"{z:.6f}")
        except (FileNotFoundError, OSError, ValueError) as exc:
            self.query_one("#structure-info", Static).update(f"[red]Error: {exc}[/red]")
