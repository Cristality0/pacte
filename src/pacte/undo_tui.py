"""Interactive TUI for undo operation selection using Textual."""

from datetime import datetime
from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import DataTable, Footer, Header, Static

from .models import Operation


class UndoSelectionApp(App[Operation | None]):
    """Textual app for selecting an operation to undo."""

    CSS = """
    Screen {
        background: $background;
    }

    #operations-table {
        height: 100%;
        border: solid $primary;
    }

    .info-text {
        padding: 1;
        background: $primary-darken-2;
        color: $text;
        text-align: center;
    }
    """

    BINDINGS: ClassVar = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, operations: list[Operation], datetime_format: str = "%H:%M:%S") -> None:
        """Initialize the undo selection app.

        Args:
            operations: List of operations to display
            datetime_format: Format string for datetime display
        """
        super().__init__()
        self.operations = operations
        self.datetime_format = datetime_format
        self.selected_operation: Operation | None = None

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()

        if not self.operations:
            yield Container(
                Static("No operations found in history", classes="info-text"),
            )
        else:
            yield VerticalScroll(
                DataTable(id="operations-table"),
            )

        yield Footer()

    def on_mount(self) -> None:
        """Set up the table when the app mounts."""
        if not self.operations:
            return

        table = self.query_one(DataTable)

        # Add columns
        table.add_columns("Time", "Type", "File", "Preview")

        # Add rows
        for operation in self.operations:
            try:
                dt = datetime.fromisoformat(operation.timestamp)
                time_str = dt.strftime(self.datetime_format)
            except (ValueError, AttributeError):
                time_str = operation.timestamp

            # Get file name from path using pathlib for cross-platform compatibility
            file_name = Path(operation.target_path).name

            # Add row
            table.add_row(
                time_str,
                operation.operation_type,
                file_name,
                operation.content_preview,
                key=operation.id,
            )

        # Set cursor
        table.cursor_type = "row"
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        if event.row_key:
            # Find the operation with this ID
            for operation in self.operations:
                if operation.id == event.row_key.value:
                    self.selected_operation = operation
                    break

            self.exit(self.selected_operation)

    def action_cancel(self) -> None:
        """Cancel selection."""
        self.exit(None)


def select_operation_to_undo(
    operations: list[Operation], datetime_format: str = "%H:%M:%S"
) -> Operation | None:
    """Show interactive TUI to select an operation to undo.

    Args:
        operations: List of operations to display
        datetime_format: Format string for datetime display

    Returns:
        Selected Operation or None if cancelled
    """
    app = UndoSelectionApp(operations, datetime_format)
    return app.run()
