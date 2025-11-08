from typing import Optional


def format_error(source: Optional[str], line: int, column: int) -> str:
    """Return a formatted error snippet showing the line and a caret at column.

    If source is None or line out of range, return a simple positional indicator.
    """
    if source is None:
        return f"Error at {line}:{column}"
    lines = source.splitlines()
    if line - 1 < 0 or line - 1 >= len(lines):
        return f"Error at {line}:{column}"
    text = lines[line - 1]
    # Column may be 1-based; ensure at least 1
    col = max(1, column)
    # Build caret line (careful with tabs)
    caret_line = " " * (col - 1) + "^"
    return f"Line {line}, Col {column}:\n{text}\n{caret_line}"
