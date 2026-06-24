"""Unit tests for the encode function of the message_cipher module."""

import pytest

from message_cipher import encode, PRINTABLE_START, PRINTABLE_END


class TestEncodeEmptyPlaintext:
    """Test that empty plaintext returns an empty string."""

    def test_empty_plaintext_returns_empty_string(self):
        assert encode("key", "") == ""

    def test_empty_plaintext_with_single_char_key(self):
        assert encode("a", "") == ""


class TestEncodeKnownPairs:
    """Test known hand-computed encode pairs using the formula:
    chr(((ord(char) - 32) + (ord(key_char) - 32 + 1)) % 95 + 32)
    """

    def test_encode_a_with_key_a(self):
        # ((97-32) + (97-32+1)) % 95 + 32 = (65 + 66) % 95 + 32 = 131 % 95 + 32 = 36 + 32 = 68 = 'D'
        assert encode("a", "a") == "D"

    def test_encode_space_with_key_space(self):
        # ((32-32) + (32-32+1)) % 95 + 32 = (0 + 1) % 95 + 32 = 1 + 32 = 33 = '!'
        assert encode(" ", " ") == "!"

    def test_encode_tilde_with_key_space(self):
        # ((126-32) + (32-32+1)) % 95 + 32 = (94 + 1) % 95 + 32 = 0 + 32 = 32 = ' '
        assert encode(" ", "~") == " "

    def test_encode_key_cycles_over_message(self):
        # Key "ab" cycles over "abc"
        # 'a' with key 'a': ((97-32)+(97-32+1))%95+32 = 68 = 'D'
        # 'b' with key 'b': ((98-32)+(98-32+1))%95+32 = (66+67)%95+32 = 133%95+32 = 38+32 = 70 = 'F'
        # 'c' with key 'a': ((99-32)+(97-32+1))%95+32 = (67+66)%95+32 = 133%95+32 = 38+32 = 70 = 'F'
        assert encode("ab", "abc") == "DFF"


class TestEncodeLengthPreservation:
    """Test that ciphertext length equals plaintext length."""

    def test_single_char(self):
        result = encode("k", "x")
        assert len(result) == 1

    def test_multiple_chars(self):
        result = encode("key", "hello")
        assert len(result) == 5

    def test_long_message(self):
        message = "a" * 100
        result = encode("secret", message)
        assert len(result) == 100


class TestEncodeOutputPrintable:
    """Test that all output characters are printable ASCII."""

    def test_all_output_chars_printable(self):
        result = encode("key", "Hello World! 123 ~`@#$%")
        for ch in result:
            assert PRINTABLE_START <= ord(ch) <= PRINTABLE_END


class TestEncodeEmptyKeyRaises:
    """Test that an empty key raises ValueError."""

    def test_empty_key_raises_value_error(self):
        with pytest.raises(ValueError, match="Key must not be empty"):
            encode("", "hello")

    def test_empty_key_with_empty_message_raises_value_error(self):
        with pytest.raises(ValueError, match="Key must not be empty"):
            encode("", "")
