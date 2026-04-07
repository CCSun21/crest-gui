"""Settings screen."""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from crest_tui.config import AppConfig, load_config, save_config

METHOD_OPTIONS = [
    ("GFN2-xTB", "gfn2"),
    ("GFN1-xTB", "gfn1"),
    ("GFN0-xTB", "gfn0"),
    ("GFN-FF", "gfnff"),
]

THEME_OPTIONS = [
    ("Dark", "dark"),
    ("Light", "light"),
]

VERBOSITY_OPTIONS = [
    ("0 - Silent", "0"),
    ("1 - Normal", "1"),
    ("2 - Verbose", "2"),
    ("3 - Debug", "3"),
]


class SettingsScreen(Screen):
    """Application settings screen."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Back", show=True)]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Settings", classes="screen-title")
        with ScrollableContainer(id="settings-form"):
            yield Label("CREST binary path:")
            yield Input(id="crest-binary", placeholder="crest")
            yield Label("xtb binary path:")
            yield Input(id="xtb-binary", placeholder="xtb")
            yield Label("Default threads:")
            yield Input(id="threads", placeholder="4")
            yield Label("Scratch directory (optional):")
            yield Input(id="scratch-dir", placeholder="/scratch/crest")
            yield Label("Default method:")
            yield Select(options=METHOD_OPTIONS, id="default-method", value="gfn2")
            yield Label("Verbosity:")
            yield Select(options=VERBOSITY_OPTIONS, id="verbosity", value="1")
            yield Label("Theme:")
            yield Select(options=THEME_OPTIONS, id="theme", value="dark")
            yield Static(id="status-msg", classes="status-msg")
            yield Button("Save", variant="success", id="btn-save")
            yield Button("Reset to Defaults", variant="error", id="btn-reset")
        yield Footer()

    def on_mount(self) -> None:
        self._load_into_form(load_config())

    def _load_into_form(self, config: AppConfig) -> None:
        self.query_one("#crest-binary", Input).value = config.crest_binary
        self.query_one("#xtb-binary", Input).value = config.xtb_binary
        self.query_one("#threads", Input).value = str(config.threads)
        self.query_one("#scratch-dir", Input).value = config.scratch_dir
        self.query_one("#default-method", Select).value = config.default_method
        self.query_one("#verbosity", Select).value = str(config.verbosity)
        self.query_one("#theme", Select).value = config.theme

    def _read_from_form(self) -> AppConfig:
        return AppConfig(
            crest_binary=self.query_one("#crest-binary", Input).value or "crest",
            xtb_binary=self.query_one("#xtb-binary", Input).value or "xtb",
            threads=int(self.query_one("#threads", Input).value or "4"),
            scratch_dir=self.query_one("#scratch-dir", Input).value,
            default_method=str(self.query_one("#default-method", Select).value),
            verbosity=int(str(self.query_one("#verbosity", Select).value)),
            theme=str(self.query_one("#theme", Select).value),
        )

    @on(Button.Pressed, "#btn-save")
    def on_save(self) -> None:
        try:
            config = self._read_from_form()
            save_config(config)
            self.app.config = config
            self.query_one("#status-msg", Static).update("[green]Settings saved.[/green]")
        except Exception as exc:
            self.query_one("#status-msg", Static).update(f"[red]Error: {exc}[/red]")

    @on(Button.Pressed, "#btn-reset")
    def on_reset(self) -> None:
        from crest_tui.config import get_default_config
        self._load_into_form(get_default_config())
        self.query_one("#status-msg", Static).update("[yellow]Defaults loaded (not saved).[/yellow]")
