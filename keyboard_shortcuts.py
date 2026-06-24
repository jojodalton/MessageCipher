"""Keyboard shortcut management for the MessageCipher application.

Handles shortcut registration, label formatting, and conflict detection
with OS-reserved key combinations.
"""

# Mapping of tkinter event sequences to application action names
SHORTCUTS: dict[str, str] = {
    "<Control-e>": "encode",
    "<Control-d>": "decode",
    "<Control-l>": "clear",
}

# OS-reserved shortcuts that the application must not override
RESERVED_SHORTCUTS: set[str] = {
    "<Control-c>",
    "<Control-v>",
    "<Control-x>",
    "<Control-z>",
}


def get_shortcut_label(action: str) -> str:
    """Return display text for a shortcut given its action name.

    Converts the tkinter event sequence into a human-readable label
    (e.g., 'Ctrl+E' for the encode action).

    Args:
        action: The action name (e.g., "encode", "decode", "clear").

    Returns:
        A formatted shortcut label like "Ctrl+E", or an empty string
        if no shortcut is mapped to the given action.
    """
    for sequence, mapped_action in SHORTCUTS.items():
        if mapped_action == action:
            # Extract the key letter from the sequence, e.g. "<Control-e>" -> "e"
            key = sequence.split("-")[-1].rstrip(">")
            return f"Ctrl+{key.upper()}"
    return ""


def is_reserved(event_sequence: str) -> bool:
    """Check if an event sequence conflicts with OS reserved shortcuts.

    Args:
        event_sequence: A tkinter event sequence string
            (e.g., "<Control-c>", "<Control-e>").

    Returns:
        True if the sequence is reserved by the OS and should not be
        overridden, False otherwise.
    """
    return event_sequence in RESERVED_SHORTCUTS
