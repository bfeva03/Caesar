from __future__ import annotations

import re


def clamp_int(value: str, lo: int, hi: int) -> int:
    """
    Parse and clamp an integer value within bounds.

    Args:
        value: String representation of integer
        lo: Minimum allowed value
        hi: Maximum allowed value

    Returns:
        Clamped integer value

    Raises:
        ValueError: If value cannot be parsed as integer
    """
    i = int(value.strip())
    return max(lo, min(hi, i))


def copy_to_clipboard(root, text: str):
    """
    Copy text to system clipboard.

    Args:
        root: Tkinter root window
        text: Text to copy
    """
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update_idletasks()


def normalize_text(s: str) -> str:
    """
    Normalize whitespace in text.

    Args:
        s: Input text

    Returns:
        Text with normalized whitespace
    """
    return re.sub(r"\s+", " ", s).strip()
