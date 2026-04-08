"""Constraint editor widget."""

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label, Select, Static

CONSTRAINT_TYPES = [
    ("Fix atoms", "fix"),
    ("Bond distance", "bond"),
    ("Angle", "angle"),
    ("Dihedral", "dihedral"),
    ("Wall potential", "wall"),
]


class ConstraintEditor(Widget):
    """Add/remove geometric constraints and generate TOML constraint block."""

    def compose(self) -> ComposeResult:
        yield Label("Constraints", classes="section-label")
        yield Select(options=CONSTRAINT_TYPES, id="constraint-type", value="fix")
        yield Label("Atom indices (comma-separated, 1-based):")
        yield Input(placeholder="1,2,3", id="atom-indices")
        yield Label("Value (distance/angle, optional):")
        yield Input(placeholder="1.5", id="constraint-value")
        yield Button("Add Constraint", variant="primary", id="btn-add-constraint")
        yield DataTable(id="constraint-table")
        yield Button("Remove Selected", variant="error", id="btn-remove-constraint")
        yield Static(id="constraint-toml", markup=True)

    def on_mount(self) -> None:
        table = self.query_one("#constraint-table", DataTable)
        table.add_columns("#", "Type", "Atoms", "Value")
        self._constraints: list[dict[str, Any]] = []

    @on(Button.Pressed, "#btn-add-constraint")
    def on_add(self) -> None:
        ctype = str(self.query_one("#constraint-type", Select).value)
        atoms_str = self.query_one("#atom-indices", Input).value.strip()
        value_str = self.query_one("#constraint-value", Input).value.strip()
        if not atoms_str:
            return
        try:
            atoms = [int(x.strip()) for x in atoms_str.split(",") if x.strip()]
        except ValueError:
            return
        value = float(value_str) if value_str else None
        entry: dict[str, Any] = {"type": ctype, "atoms": atoms}
        if value is not None:
            entry["value"] = value
        self._constraints.append(entry)
        self._refresh_table()
        self._refresh_toml()

    @on(Button.Pressed, "#btn-remove-constraint")
    def on_remove(self) -> None:
        table = self.query_one("#constraint-table", DataTable)
        if table.cursor_row >= 0 and self._constraints:
            idx = table.cursor_row
            if 0 <= idx < len(self._constraints):
                self._constraints.pop(idx)
                self._refresh_table()
                self._refresh_toml()

    def _refresh_table(self) -> None:
        table = self.query_one("#constraint-table", DataTable)
        table.clear()
        for i, c in enumerate(self._constraints, start=1):
            atoms_str = ",".join(str(a) for a in c["atoms"])
            value_str = str(c.get("value", ""))
            table.add_row(str(i), c["type"], atoms_str, value_str)

    def _refresh_toml(self) -> None:
        if not self._constraints:
            self.query_one("#constraint-toml", Static).update("")
            return
        lines = ["[calculation.constraints]"]
        for c in self._constraints:
            atoms_str = ", ".join(str(a) for a in c["atoms"])
            if "value" in c:
                lines.append(f'  {{ type = "{c["type"]}", atoms = [{atoms_str}], value = {c["value"]} }}')
            else:
                lines.append(f'  {{ type = "{c["type"]}", atoms = [{atoms_str}] }}')
        toml_text = "\n".join(lines)
        self.query_one("#constraint-toml", Static).update(f"[dim]{toml_text}[/dim]")

    def get_constraints(self) -> list[dict[str, Any]]:
        """Return current list of constraint dicts."""
        return list(self._constraints)

    def get_toml_block(self) -> dict:
        """Return constraints as a TOML-compatible dict."""
        return {"constraints": self._constraints}
