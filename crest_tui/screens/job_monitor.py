"""Job monitor screen for streaming CREST output."""

import uuid
from datetime import datetime

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, RichLog, Static

from crest_tui.runner import Job, JobRunner, JobStatus


_runner = JobRunner()


class JobMonitorScreen(Screen):
    """Displays streaming job output and status."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", show=True),
        Binding("ctrl+c", "cancel_job", "Cancel", show=True),
    ]

    def __init__(self, command: list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._command = command or []
        self._current_job: Job | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Job Monitor", classes="screen-title")
        with Horizontal(id="status-bar"):
            yield Static("Status: [dim]idle[/dim]", id="job-status", markup=True)
            yield Static("", id="job-timer", markup=True)
        yield RichLog(id="output-log", wrap=True, markup=False, highlight=True)
        with Horizontal(classes="button-row"):
            yield Button("Cancel", variant="error", id="btn-cancel")
            yield Button("Clear", variant="default", id="btn-clear")
            yield Button("Back", variant="default", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        if self._command:
            self._start_job(self._command)

    def _start_job(self, command: list[str]) -> None:
        job = Job(id=str(uuid.uuid4()), command=command)
        _runner.register_job(job)
        self._current_job = job
        self._run_job_async(job)

    @work(exclusive=True)
    async def _run_job_async(self, job: Job) -> None:
        self.query_one("#job-status", Static).update(
            f"Status: [yellow]running[/yellow]  Command: [dim]{' '.join(job.command[:3])}...[/dim]"
        )
        log = self.query_one("#output-log", RichLog)

        def on_line(line: str) -> None:
            log.write(line)

        await _runner.run_job(job, output_callback=on_line)

        end_str = datetime.now().strftime("%H:%M:%S")
        if job.status == JobStatus.COMPLETED:
            self.query_one("#job-status", Static).update(
                f"Status: [green]completed[/green]  finished at {end_str}"
            )
        elif job.status == JobStatus.CANCELLED:
            self.query_one("#job-status", Static).update(
                f"Status: [yellow]cancelled[/yellow]  at {end_str}"
            )
        else:
            self.query_one("#job-status", Static).update(
                f"Status: [red]failed[/red] (rc={job.returncode})  at {end_str}"
            )

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self) -> None:
        if self._current_job:
            _runner.cancel_job(self._current_job)

    @on(Button.Pressed, "#btn-clear")
    def on_clear(self) -> None:
        self.query_one("#output-log", RichLog).clear()

    @on(Button.Pressed, "#btn-back")
    def on_back(self) -> None:
        self.app.pop_screen()

    def action_cancel_job(self) -> None:
        self.on_cancel()
