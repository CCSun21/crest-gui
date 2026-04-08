"""ASCII energy bar chart widget."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static

KCAL_PER_EH = 627.5094740631
BAR_CHAR = "█"
MAX_WIDTH = 40


class EnergyPlot(Widget):
    """Renders an ASCII bar chart of conformer energies."""

    def compose(self) -> ComposeResult:
        yield Static(id="energy-chart", markup=True)

    def plot(self, energies: list[float], unit: str = "kcal/mol") -> None:
        """Render bar chart from list of energies."""
        chart = self.query_one("#energy-chart", Static)
        if not energies:
            chart.update("[dim]No energies to display.[/dim]")
            return

        # Convert to relative energies
        min_e = min(energies)
        rel = [e - min_e for e in energies]
        max_rel = max(rel) if max(rel) > 0 else 1.0

        lines = [f"[bold]Conformer energies (relative, {unit})[/bold]", ""]
        for i, (e, r) in enumerate(zip(energies, rel), start=1):
            bar_len = int((r / max_rel) * MAX_WIDTH)
            bar = BAR_CHAR * bar_len
            lines.append(f"{i:>4}  {bar:<{MAX_WIDTH}}  {r:6.2f}")

        lines.append("")
        lines.append(f"Min energy: {min_e:.6f} {unit}")
        chart.update("\n".join(lines))

    def plot_from_ensemble(self, path: str) -> None:
        """Load ensemble file and plot relative energies in kcal/mol."""
        from crest_tui.parser import parse_xyz_ensemble

        try:
            conformers = parse_xyz_ensemble(path)
            energies_eh = [c["energy"] for c in conformers if c["energy"] is not None]
            if not energies_eh:
                self.query_one("#energy-chart", Static).update("[red]No energies found.[/red]")
                return
            energies_kcal = [e * KCAL_PER_EH for e in energies_eh]
            self.plot(energies_kcal)
        except (FileNotFoundError, OSError, ValueError) as exc:
            self.query_one("#energy-chart", Static).update(f"[red]Error: {exc}[/red]")
