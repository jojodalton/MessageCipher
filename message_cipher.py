"""Message cipher module implementing a modified Vigenère cipher over printable ASCII."""

PRINTABLE_START = 32   # Space character
PRINTABLE_END = 126    # Tilde character
PRINTABLE_RANGE = PRINTABLE_END - PRINTABLE_START + 1  # 95 printable characters


def _validate_inputs(key, text, param_name):
    """Validate key and text inputs in order: key type → text type → key emptiness → char range.

    Args:
        key: The encryption/decryption key (must be a non-empty string of printable ASCII).
        text: The text to encode/decode (must be a string of printable ASCII).
        param_name: Name of the text parameter for error messages.

    Raises:
        TypeError: If key is not a string, or text is not a string.
        ValueError: If key is an empty string or contains non-printable-ASCII characters.
    """
    if not isinstance(key, str):
        raise TypeError("Key must be a string")
    if not isinstance(text, str):
        raise TypeError(f"{param_name} must be a string")
    if len(key) == 0:
        raise ValueError("Key must not be empty")
    for i, ch in enumerate(key):
        if not (PRINTABLE_START <= ord(ch) <= PRINTABLE_END):
            raise ValueError(
                f"Key contains non-printable-ASCII character {ch!r} (code {ord(ch)}) at position {i}. "
                f"Only characters in range 32-126 are allowed."
            )
    for i, ch in enumerate(text):
        if not (PRINTABLE_START <= ord(ch) <= PRINTABLE_END):
            raise ValueError(
                f"{param_name} contains non-printable-ASCII character {ch!r} (code {ord(ch)}) at position {i}. "
                f"Only characters in range 32-126 are allowed."
            )


def _shift_char(char, key_char, direction):
    """Shift a single character within the printable ASCII range (32-126).

    Uses the formula:
        ((ord(char) - 32) + direction * ((ord(key_char) - 32) % 94 + 1)) % 95 + 32

    The shift amount is ((key_ord - 32) % 94 + 1), which guarantees a value
    in range [1, 94] — never 0 or 95 — so no character maps to itself.

    Args:
        char: The character to shift (must be in printable ASCII range).
        key_char: The key character determining the shift amount.
        direction: +1 for encoding, -1 for decoding.

    Returns:
        The shifted character (always printable ASCII).
    """
    shift = (ord(key_char) - PRINTABLE_START) % (PRINTABLE_RANGE - 1) + 1  # Always 1..94
    offset = (ord(char) - PRINTABLE_START + direction * shift) % PRINTABLE_RANGE
    return chr(offset + PRINTABLE_START)


def _apply_cipher(key, text, direction):
    """Apply the cipher to the full text by cycling the key.

    Args:
        key: The encryption/decryption key.
        text: The text to process.
        direction: +1 for encoding, -1 for decoding.

    Returns:
        The transformed text.
    """
    key_len = len(key)
    return "".join(
        _shift_char(char, key[i % key_len], direction)
        for i, char in enumerate(text)
    )


def encode(key, message):
    """Encode a plaintext message using the given key.

    Both key and message must contain only printable ASCII characters (32-126).

    Args:
        key: The encryption key (must be a non-empty string of printable ASCII).
        message: The plaintext message to encode (must be a string of printable ASCII).

    Returns:
        The ciphertext of the same length as the message (all printable ASCII).

    Raises:
        TypeError: If key is not a string, or message is not a string.
        ValueError: If key is an empty string or contains non-printable characters.
    """
    _validate_inputs(key, message, "message")
    if message == "":
        return ""
    return _apply_cipher(key, message, +1)


def decode(key, ciphertext):
    """Decode a ciphertext using the given key.

    Both key and ciphertext must contain only printable ASCII characters (32-126).

    Args:
        key: The decryption key (must be a non-empty string of printable ASCII).
        ciphertext: The ciphertext to decode (must be a string of printable ASCII).

    Returns:
        The original plaintext of the same length as the ciphertext.

    Raises:
        TypeError: If key is not a string, or ciphertext is not a string.
        ValueError: If key is an empty string or contains non-printable characters.
    """
    _validate_inputs(key, ciphertext, "ciphertext")
    if ciphertext == "":
        return ""
    return _apply_cipher(key, ciphertext, -1)
