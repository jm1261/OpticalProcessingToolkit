from __future__ import annotations

import argparse
from pathlib import Path


LOG_FILE_PREFIX = "application_"
RETAIN_MARKERS = ("ERROR", "WARNING", "FAILURE", "FAILED")


def contains_retain_marker(log_file: Path) -> bool:
    """
    Return whether a log file contains a marker that should retain it.

    Args:
        log_file: Log file to inspect.

    Returns:
        True when the file contains a configured retention marker.

    Raises:
        OSError: If the file cannot be read.
    """
    contents = log_file.read_text(encoding="utf-8", errors="replace").upper()
    return any(marker in contents for marker in RETAIN_MARKERS)


def cleanup_logs(log_directory: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Delete clean application logs and report deleted and retained counts.

    Args:
        log_directory: Directory containing application log files.
        dry_run: Report deletions without removing files when True.

    Returns:
        A tuple containing deleted-or-previewed and retained file counts.

    Side effects:
        Prints one status line for each processed file.

    Raises:
        OSError: If a matching file cannot be inspected or deleted.
    """
    deleted = 0
    retained = 0

    for log_file in sorted(log_directory.glob(f"{LOG_FILE_PREFIX}*")):
        if not log_file.is_file():
            continue

        if contains_retain_marker(log_file):
            retained += 1
            print(f"Retained: {log_file.name}")
            continue

        if not dry_run:
            log_file.unlink()
        deleted += 1
        action = "Would delete" if dry_run else "Deleted"
        print(f"{action}: {log_file.name}")

    return deleted, retained


def main() -> None:
    """Parse options and run cleanup in the Raman logging directory.

    Raises:
        OSError: If a matching log file cannot be inspected or deleted.
        SystemExit: If command-line arguments are invalid.

    Side effects:
        Deletes matching files without retention markers unless `--dry-run` is
        supplied, and prints cleanup status and summary lines.
    """
    parser = argparse.ArgumentParser(
        description="Delete application log files without errors or failure warnings."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be deleted without removing them.",
    )
    args = parser.parse_args()

    log_directory = Path(__file__).resolve().parent
    deleted, retained = cleanup_logs(log_directory, dry_run=args.dry_run)
    action = "would be deleted" if args.dry_run else "deleted"
    print(f"{deleted} file(s) {action}; {retained} file(s) retained.")


if __name__ == "__main__":
    main()
