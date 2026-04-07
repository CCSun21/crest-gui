"""QCG solvation screen."""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, RichLog, Select

from crest_tui.command_builder import build_legacy_command, preview_command
from crest_tui.config import AppConfig
from crest_tui.toml_builder import QCGParams, build_qcg_toml, toml_to_string

METHOD_OPTIONS = [
    ("GFN2-xTB (default)", "gfn2"),
    ("GFN1-xTB", "gfn1"),
    ("GFN0-xTB", "gfn0"),
    ("GFN-FF", "gfnff"),
]


class QCGScreen(Screen):
    """Form for QCG solvation calculation."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Back", show=True)]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("QCG Quantum Cluster Growth", classes="screen-title")
        with Horizontal(id="main-layout"):
            with ScrollableContainer(id="form-panel"):
                yield Label("Solute structure file:")
                yield Input(placeholder="solute.xyz", id="input-file")
                yield Label("Solvent structure file:")
                yield Input(placeholder="solvent.xyz", id="solvent-file")
                yield Label("Method:")
                yield Select(options=METHOD_OPTIONS, id="method", value="gfn2")
                yield Label("Charge:")
                yield Input(placeholder="0", value="0", id="charge")
                yield Label("UHF:")
                yield Input(placeholder="0", value="0", id="uhf")
                yield Label("Number of solvent molecules:")
                yield Input(placeholder="5", value="5", id="nsolv")
                yield Label("Threads:")
                yield Input(placeholder="4", value="4", id="threads")
                yield Checkbox("Ensemble mode", id="ensemble")
                yield Label("Extra flags:")
                yield Input(placeholder="", id="extra-flags")
                with Horizontal(classes="button-row"):
                    yield Button("Run", variant="success", id="btn-run")
                    yield Button("Dry Run", variant="primary", id="btn-dry")
                    yield Button("Back", variant="default", id="btn-back")
            with Vertical(id="preview-panel"):
                yield Label("Preview:", classes="section-label")
                yield RichLog(id="preview-log", wrap=True, markup=True)
        yield Footer()

    def _get_params(self) -> QCGParams:
        return QCGParams(
            input_file=self.query_one("#input-file", Input).value,
            solvent_file=self.query_one("#solvent-file", Input).value,
            method=str(self.query_one("#method", Select).value),
            charge=int(self.query_one("#charge", Input).value or "0"),
            uhf=int(self.query_one("#uhf", Input).value or "0"),
            nsolv=int(self.query_one("#nsolv", Input).value or "5"),
            threads=int(self.query_one("#threads", Input).value or "4"),
            ensemble=self.query_one("#ensemble", Checkbox).value,
            extra_flags=self.query_one("#extra-flags", Input).value,
        )

    def _update_preview(self, dry_run: bool = False) -> None:
        try:
            params = self._get_params()
            toml_str = toml_to_string(build_qcg_toml(params))
            config = getattr(self.app, "config", AppConfig())
            extra = params.extra_flags.split() if params.extra_flags else []
            cmd = build_legacy_command(
                params.input_file or "solute.xyz",
                "qcg",
                params.method,
                params.charge,
                params.uhf,
                params.threads,
                extra_flags=extra,
                dry_run=dry_run,
                crest_binary=config.crest_binary,
            )
            log = self.query_one("#preview-log", RichLog)
            log.clear()
            log.write("[bold cyan]--- TOML ---[/bold cyan]")
            log.write(toml_str)
            log.write("[bold cyan]--- Command ---[/bold cyan]")
            log.write(preview_command(cmd))
        except (ValueError, TypeError):
            pass

    @on(Input.Changed)
    def on_input_changed(self, _: Input.Changed) -> None:
        self._update_preview()

    @on(Select.Changed)
    def on_select_changed(self, _: Select.Changed) -> None:
        self._update_preview()

    @on(Checkbox.Changed)
    def on_checkbox_changed(self, _: Checkbox.Changed) -> None:
        self._update_preview()

    @on(Button.Pressed, "#btn-run")
    def on_run(self) -> None:
        self._update_preview()
        self.app.push_screen("job_monitor")

    @on(Button.Pressed, "#btn-dry")
    def on_dry(self) -> None:
        self._update_preview(dry_run=True)

    @on(Button.Pressed, "#btn-back")
    def on_back(self) -> None:
        self.app.pop_screen()
