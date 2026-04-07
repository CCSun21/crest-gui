"""File picker widget."""

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DirectoryTree, Input, Label, Static


class FilePicker(Widget):
    """Browse files with optional extension filtering."""

    selected_path: reactive[str] = reactive("")

    def __init__(self, extensions: list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._extensions = [ext.lower() for ext in (extensions or [])]

    def compose(self) -> ComposeResult:
        yield Label("Browse files:")
        yield Input(
            value=str(Path.cwd()),
            placeholder="Directory path",
            id="dir-input",
        )
        yield DirectoryTree(str(Path.cwd()), id="dir-tree")
        yield Static(id="selected-label", markup=True)

    @on(Input.Submitted, "#dir-input")
    def on_dir_input(self, event: Input.Submitted) -> None:
        path = Path(event.value)
        if path.is_dir():
            self.query_one("#dir-tree", DirectoryTree).path = path

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        path = event.path
        if self._extensions:
            if path.suffix.lower() not in self._extensions:
                return
        self.selected_path = str(path)
        self.query_one("#selected-label", Static).update(f"[green]Selected:[/green] {path}")
        self.post_message(self.FileChosen(self, str(path)))

    class FileChosen(Widget.Message):
        """Message emitted when a file is chosen."""

        def __init__(self, widget: "FilePicker", path: str) -> None:
            super().__init__()
            self.widget = widget
            self.path = path
