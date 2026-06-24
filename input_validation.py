"""Pure validation functions for the MessageCipher modern UI.

This module provides character validation, key validation, character counting,
copy eligibility checks, and status message truncation — all independent of
the GUI layer for easy testing.
"""

PRINTABLE_START = 32
PRINTABLE_END = 126


def is_printable_ascii(ch: str) -> bool:
    """Check if a single character is in printable ASCII range (32-126)."""
    if len(ch) != 1:
        return False
    code = ord(ch)
    return PRINTABLE_START <= code <= PRINTABLE_END


def find_forbidden_positions(text: str, allow_newline: bool = True) -> list[int]:
    """Return indices of all characters outside printable ASCII range.

    Args:
        text: The text to scan.
        allow_newline: If True, newline characters are not considered forbidden.

    Returns:
        List of 0-based indices where forbidden characters occur.
    """
    forbidden = []
    for i, ch in enumerate(text):
        code = ord(ch)
        if code < PRINTABLE_START or code > PRINTABLE_END:
            if allow_newline and ch == '\n':
                continue
            forbidden.append(i)
    return forbidden


def is_valid_key(key: str) -> tuple[bool, str]:
    """Validate a cipher key.

    Returns:
        (True, "") if valid, (False, error_message) if invalid.
    """
    if not key:
        return (False, "Key must not be empty")
    if len(key) > 1000:
        return (False, "Key must be at most 1000 characters")
    for ch in key:
        if not is_printable_ascii(ch):
            return (False, "Key contains non-printable ASCII characters")
    return (True, "")


def count_characters(text: str) -> int:
    """Count characters in text excluding trailing newline.

    Matches the character count display requirement: includes all characters
    in the text area content excluding the trailing newline.
    """
    if not text:
        return 0
    if text.endswith('\n'):
        return len(text) - 1
    return len(text)


def is_copy_eligible(text: str) -> bool:
    """Check if text contains at least one non-whitespace character.

    Used by copy-to-clipboard to determine if copy should proceed.
    """
    return bool(text) and not text.isspace()


def truncate_status_message(message: str, max_length: int = 200) -> str:
    """Truncate a status message to max_length characters."""
    if len(message) <= max_length:
        return message
    return message[:max_length]
