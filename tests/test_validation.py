"""Unit tests for input validation and error handling.

Validates Requirements 5.1, 5.2, 5.3:
- TypeError for non-string key
- TypeError for non-string message/ciphertext with appropriate param name
- Key validation takes priority when both key and text are invalid
"""

import pytest

from message_cipher import encode, decode


# --- Requirement 5.1: Non-string key raises TypeError ---


@pytest.mark.parametrize("invalid_key", [None, 123, [1, 2, 3]])
class TestInvalidKeyType:
    """Non-string values as key raise TypeError with key message."""

    def test_encode_invalid_key_raises_type_error(self, invalid_key):
        with pytest.raises(TypeError, match="Key must be a string"):
            encode(invalid_key, "hello")

    def test_decode_invalid_key_raises_type_error(self, invalid_key):
        with pytest.raises(TypeError, match="Key must be a string"):
            decode(invalid_key, "hello")


# --- Requirement 5.2: Non-string message/ciphertext raises TypeError ---


@pytest.mark.parametrize("invalid_text", [None, 123, [1, 2, 3]])
class TestInvalidTextType:
    """Non-string values as message/ciphertext raise TypeError with param name."""

    def test_encode_invalid_message_raises_type_error(self, invalid_text):
        with pytest.raises(TypeError, match="message must be a string"):
            encode("key", invalid_text)

    def test_decode_invalid_ciphertext_raises_type_error(self, invalid_text):
        with pytest.raises(TypeError, match="ciphertext must be a string"):
            decode("key", invalid_text)


# --- Requirement 5.3: Key validated first when both are invalid ---


@pytest.mark.parametrize("invalid_key,invalid_text", [
    (None, None),
    (123, 123),
    ([1, 2], [3, 4]),
    (123, None),
])
class TestKeyValidationPriority:
    """When both key and text are invalid, TypeError for key is raised first."""

    def test_encode_key_error_before_message_error(self, invalid_key, invalid_text):
        with pytest.raises(TypeError, match="Key must be a string"):
            encode(invalid_key, invalid_text)

    def test_decode_key_error_before_ciphertext_error(self, invalid_key, invalid_text):
        with pytest.raises(TypeError, match="Key must be a string"):
            decode(invalid_key, invalid_text)
