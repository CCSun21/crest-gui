"""Main CREST TUI application."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from crest_tui.config import load_config
from crest_tui.screens.dashboard import DashboardScreen
from crest_tui.screens.conformer_search import ConformerSearchScreen
from crest_tui.screens.entropy import EntropyScreen
from crest_tui.screens.constrained import ConstrainedScreen
from crest_tui.screens.protonation import ProtonationScreen
from crest_tui.screens.nci import NCIScreen
from crest_tui.screens.qcg import QCGScreen
from crest_tui.screens.msreact import MSREACTScreen
from crest_tui.screens.optimization import OptimizationScreen
from crest_tui.screens.dynamics import DynamicsScreen
from crest_tui.screens.cregen import CREGENScreen
from crest_tui.screens.settings import SettingsScreen
from crest_tui.screens.job_monitor import JobMonitorScreen


class CrestApp(App):
    """CREST Terminal User Interface."""

    CSS_PATH = Path(__file__).parent / "styles" / "crest.tcss"

    TITLE = "CREST TUI"
    SUB_TITLE = "Conformer-Rotamer Ensemble Sampling Tool"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+d", "show_dashboard", "Dashboard", show=True),
        Binding("ctrl+s", "show_settings", "Settings", show=True),
        Binding("ctrl+j", "show_job_monitor", "Jobs", show=True),
        Binding("f1", "show_dashboard", "Dashboard", show=False),
    ]

    SCREENS = {
        "dashboard": DashboardScreen,
        "conformer_search": ConformerSearchScreen,
        "entropy": EntropyScreen,
        "constrained": ConstrainedScreen,
        "protonation": ProtonationScreen,
        "nci": NCIScreen,
        "qcg": QCGScreen,
        "msreact": MSREACTScreen,
        "optimization": OptimizationScreen,
        "dynamics": DynamicsScreen,
        "cregen": CREGENScreen,
        "settings": SettingsScreen,
        "job_monitor": JobMonitorScreen,
    }

    def on_mount(self) -> None:
        self.config = load_config()
        self.push_screen("dashboard")

    def action_show_dashboard(self) -> None:
        self.push_screen("dashboard")

    def action_show_settings(self) -> None:
        self.push_screen("settings")

    def action_show_job_monitor(self) -> None:
        self.push_screen("job_monitor")

    def action_show_conformer_search(self) -> None:
        self.push_screen("conformer_search")

    def action_show_entropy(self) -> None:
        self.push_screen("entropy")

    def action_show_constrained(self) -> None:
        self.push_screen("constrained")

    def action_show_protonation(self) -> None:
        self.push_screen("protonation")

    def action_show_nci(self) -> None:
        self.push_screen("nci")

    def action_show_qcg(self) -> None:
        self.push_screen("qcg")

    def action_show_msreact(self) -> None:
        self.push_screen("msreact")

    def action_show_optimization(self) -> None:
        self.push_screen("optimization")

    def action_show_dynamics(self) -> None:
        self.push_screen("dynamics")

    def action_show_cregen(self) -> None:
        self.push_screen("cregen")


def main() -> None:
    """Entry point for the CREST TUI."""
    app = CrestApp()
    app.run()


if __name__ == "__main__":
    main()
