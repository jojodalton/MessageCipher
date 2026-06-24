"""Unit tests for the decode function of the message_cipher module."""

import pytest

from message_cipher import decode, encode


class TestDecodeEmptyCiphertext:
    """Tests for decoding empty ciphertext."""

    def test_empty_ciphertext_returns_empty_string(self):
        assert decode("secret", "") == ""

    def test_empty_ciphertext_with_single_char_key(self):
        assert decode("k", "") == ""


class TestDecodeKnownPairs:
    """Tests for known encode/decode pairs."""

    def test_decode_reverses_encode(self):
        ciphertext = encode("a", "a")
        assert ciphertext == "D"
        assert decode("a", "D") == "a"

    def test_decode_multi_char_message(self):
        key = "key"
        plaintext = "hello"
        ciphertext = encode(key, plaintext)
        assert decode(key, ciphertext) == plaintext

    def test_decode_with_spaces_and_punctuation(self):
        key = "secret"
        plaintext = "Hello, World!"
        ciphertext = encode(key, plaintext)
        assert decode(key, ciphertext) == plaintext

    def test_decode_deterministic(self):
        key = "mykey"
        ciphertext = encode(key, "test message")
        result1 = decode(key, ciphertext)
        result2 = decode(key, ciphertext)
        assert result1 == result2


class TestDecodeEmptyKeyRaises:
    """Tests for empty key raising ValueError."""

    def test_empty_key_raises_value_error(self):
        with pytest.raises(ValueError, match="Key must not be empty"):
            decode("", "some ciphertext")

    def test_empty_key_with_empty_ciphertext_raises_value_error(self):
        with pytest.raises(ValueError, match="Key must not be empty"):
            decode("", "")


class TestDecodeWrongKey:
    """Tests for wrong key producing wrong result."""

    def test_wrong_key_does_not_recover_plaintext(self):
        key = "correct"
        wrong_key = "wrong!!"
        plaintext = "secret message"
        ciphertext = encode(key, plaintext)
        result = decode(wrong_key, ciphertext)
        assert result != plaintext

    def test_wrong_key_single_char_difference(self):
        key = "abc"
        wrong_key = "abd"
        plaintext = "hello world"
        ciphertext = encode(key, plaintext)
        result = decode(wrong_key, ciphertext)
        assert result != plaintext
