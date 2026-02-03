"""CLI commands for Pacte."""

import sys
from pathlib import Path

import typer
from rich.console import Console

from .clipboard import get_clipboard_content, set_clipboard_content
from .config import load_config
from .exceptions import (
    ClipboardError,
    EmptyClipboardError,
    FileOperationError,
    HistoryError,
    PacteError,
)
from .file_operations import (
    append_to_file,
    create_backup,
    delete_file,
    is_binary_file,
    read_from_file,
    restore_from_backup,
    write_to_file,
)
from .history import HistoryManager
from .undo_tui import select_operation_to_undo
from .utils import format_file_size

app = typer.Typer(
    name="pacte",
    help="Cross-platform CLI clipboard management tool",
    no_args_is_help=True,
)
console = Console()


def handle_error(error: Exception, exit_code: int = 1) -> None:
    """Handle and display error with appropriate exit code.

    Args:
        error: The exception to handle
        exit_code: Exit code to use
    """
    console.print(f"[bold red]Error:[/bold red] {error}")
    sys.exit(exit_code)


@app.command(name="paste")
def paste_command(
    file_path: Path = typer.Argument(..., help="Target file path"),
    no_backup: bool = typer.Option(False, "--no-backup", help="Skip backup creation"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite without confirmation"),
    no_create: bool = typer.Option(
        False, "--no-create", help="Fail if file doesn't exist instead of creating it"
    ),
) -> None:
    """Paste clipboard content to a file.

    Creates the file and parent directories if they don't exist (unless --no-create is specified).
    Overwrites the file if it exists (with backup by default).
    """
    try:
        config = load_config()

        file_exists = file_path.exists()
        parent_exists = file_path.parent.exists()

        # Check if file doesn't exist and --no-create is specified
        if not file_exists and no_create:
            raise FileOperationError(
                f"File does not exist: {file_path}. Use without --no-create to create it."
            )

        # Check if file exists and prompt if not force
        if file_exists and not force:
            confirm = typer.confirm(f"File '{file_path}' already exists. Overwrite?", default=False)
            if not confirm:
                console.print("[yellow]Operation cancelled[/yellow]")
                sys.exit(5)

        # Get clipboard content
        content = get_clipboard_content()

        # Create backup if needed
        backup_path = None
        if file_exists and (config.backup_on_paste and not no_backup):
            backup_path = create_backup(file_path)
            console.print(f"[green]>[/green] Backed up to '{backup_path.name}'")

        # Create parent directories if they don't exist
        if not parent_exists:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]>[/green] Created directory '{file_path.parent}'")

        # Write to file
        size = write_to_file(file_path, content, encoding=config.default_encoding)

        # Notify if file was created
        if not file_exists:
            console.print(f"[green]>[/green] Created file '{file_path}'")

        # Record in history
        history = HistoryManager(max_history=config.max_history)
        history.add_operation(
            operation_type="paste",
            target_path=file_path,
            backup_path=backup_path,
            content_preview=content,
        )

        console.print(
            f"[green]>[/green] Pasted clipboard content to '{file_path}' ({format_file_size(size)})"
        )

    except EmptyClipboardError as e:
        handle_error(e, exit_code=2)
    except ClipboardError as e:
        handle_error(e, exit_code=2)
    except FileOperationError as e:
        handle_error(e, exit_code=3)
    except HistoryError as e:
        handle_error(e, exit_code=4)
    except PacteError as e:
        handle_error(e, exit_code=1)


@app.command(name="append")
def append_command(
    file_path: Path = typer.Argument(..., help="Target file path"),
    no_newline: bool = typer.Option(False, "--no-newline", help="Don't add newline"),
    no_backup: bool = typer.Option(False, "--no-backup", help="Skip backup creation"),
) -> None:
    """Append clipboard content to a file.

    Adds a newline before the content by default.
    """
    try:
        config = load_config()

        # Get clipboard content
        content = get_clipboard_content()

        # Create backup if file exists and backup enabled
        backup_path = None
        if file_path.exists() and (config.backup_on_append and not no_backup):
            backup_path = create_backup(file_path)
            console.print(f"[green]>[/green] Backed up to '{backup_path.name}'")

        # Append to file
        size = append_to_file(
            file_path,
            content,
            add_newline=not no_newline,
            encoding=config.default_encoding,
        )

        # Record in history
        history = HistoryManager(max_history=config.max_history)
        history.add_operation(
            operation_type="append",
            target_path=file_path,
            backup_path=backup_path,
            content_preview=content,
        )

        console.print(
            f"[green]>[/green] Appended clipboard content to '{file_path}' "
            f"({format_file_size(size)})"
        )

    except EmptyClipboardError as e:
        handle_error(e, exit_code=2)
    except ClipboardError as e:
        handle_error(e, exit_code=2)
    except FileOperationError as e:
        handle_error(e, exit_code=3)
    except HistoryError as e:
        handle_error(e, exit_code=4)
    except PacteError as e:
        handle_error(e, exit_code=1)


@app.command(name="copy")
def copy_command(
    file_path: Path = typer.Argument(..., help="Source file path"),
    encoding: str = typer.Option("utf-8", "--encoding", help="File encoding"),
) -> None:
    """Copy file content to clipboard."""
    try:
        # Check if binary file
        if is_binary_file(file_path):
            console.print(
                "[yellow]Warning:[/yellow] File appears to be binary. May not copy correctly."
            )
            confirm = typer.confirm("Continue?", default=False)
            if not confirm:
                console.print("[yellow]Operation cancelled[/yellow]")
                sys.exit(5)

        # Read file
        content = read_from_file(file_path, encoding=encoding)

        # Copy to clipboard
        set_clipboard_content(content)

        size = file_path.stat().st_size
        console.print(
            f"[green]>[/green] Copied '{file_path}' to clipboard ({format_file_size(size)})"
        )

    except ClipboardError as e:
        handle_error(e, exit_code=2)
    except FileOperationError as e:
        handle_error(e, exit_code=3)
    except PacteError as e:
        handle_error(e, exit_code=1)


@app.command(name="undo")
def undo_command(
    last: bool = typer.Option(False, "--last", help="Undo last operation without prompt"),
    list_history: bool = typer.Option(False, "--list", help="List operation history"),
) -> None:
    """Undo a paste or append operation.

    Shows an interactive TUI to select which operation to undo.
    """
    try:
        config = load_config()
        history = HistoryManager(max_history=config.max_history)

        operations = history.get_operations(limit=50)

        if not operations:
            console.print("[yellow]No operations found in history[/yellow]")
            return

        # List mode
        if list_history:
            console.print("[bold]Operation History:[/bold]\n")
            for i, op in enumerate(operations, 1):
                console.print(f"{i}. [{op.operation_type}] {op.target_path} - {op.content_preview}")
            return

        # Select operation
        if last:
            selected_operation = operations[0]
        else:
            selected_operation = select_operation_to_undo(
                operations, datetime_format=config.datetime_format
            )

        if not selected_operation:
            console.print("[yellow]Operation cancelled[/yellow]")
            sys.exit(5)

        # Perform undo
        target_path = Path(selected_operation.target_path)

        if selected_operation.backup_path:
            # Restore from backup
            backup_path = Path(selected_operation.backup_path)
            restore_from_backup(backup_path, target_path)
            console.print(f"[green]>[/green] Restored '{target_path}' from backup")
        else:
            # Delete file (it was newly created)
            delete_file(target_path)
            console.print(f"[green]>[/green] Deleted '{target_path}'")

        # Remove from history
        history.remove_operation(selected_operation.id)
        console.print("[green]>[/green] Operation removed from history")

    except FileOperationError as e:
        handle_error(e, exit_code=3)
    except HistoryError as e:
        handle_error(e, exit_code=4)
    except PacteError as e:
        handle_error(e, exit_code=1)


if __name__ == "__main__":
    app()
