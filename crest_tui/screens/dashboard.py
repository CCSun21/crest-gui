"""Dashboard screen - main entry point of the CREST TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static


CREST_LOGO = r"""
  ██████╗██████╗ ███████╗███████╗████████╗
 ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝
 ██║     ██████╔╝█████╗  ███████╗   ██║
 ██║     ██╔══██╗██╔══╝  ╚════██║   ██║
 ╚██████╗██║  ██║███████╗███████║   ██║
  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝
  Conformer-Rotamer Ensemble Sampling Tool
"""

WORKFLOWS = [
    ("conformer_search", "iMTD-GC Conformer Search", "Full conformational sampling"),
    ("entropy",          "Entropy / Thermo",         "Thermodynamic ensemble properties"),
    ("constrained",      "Constrained Search",        "Sampling with geometric constraints"),
    ("protonation",      "Protonation / Deprotonation", "Site enumeration"),
    ("nci",              "NCI Search",               "Non-covalent interaction complexes"),
    ("qcg",              "QCG Solvation",            "Quantum cluster growth"),
    ("msreact",          "MS/React",                 "Mass-spec reaction pathways"),
    ("optimization",     "Structure Optimization",   "Single-structure optimization"),
    ("dynamics",         "Molecular Dynamics",       "MD trajectory generation"),
    ("cregen",           "CREGEN Sorting",           "Ensemble filtering & sorting"),
]


class DashboardScreen(Screen):
    """Main dashboard showing available CREST workflows."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(CREST_LOGO, id="logo", classes="logo")
        yield Label("Select a workflow:", id="workflow-label", classes="section-label")
        yield ListView(
            *[
                ListItem(
                    Label(f"[bold]{label}[/bold]  [dim]{desc}[/dim]", markup=True),
                    id=f"workflow-{screen_id}",
                )
                for screen_id, label, desc in WORKFLOWS
            ],
            id="workflow-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id: str = event.item.id or ""
        if item_id.startswith("workflow-"):
            screen_name = item_id[len("workflow-"):]
            self.app.push_screen(screen_name)
