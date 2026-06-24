"""Property-based tests for the message cipher module using Hypothesis.

All tests operate within printable ASCII range (32-126).
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from message_cipher import encode, decode, PRINTABLE_START, PRINTABLE_END

# Strategy for printable ASCII text
printable_ascii = st.text(
    alphabet=st.characters(min_codepoint=PRINTABLE_START, max_codepoint=PRINTABLE_END),
)
printable_ascii_nonempty = st.text(
    alphabet=st.characters(min_codepoint=PRINTABLE_START, max_codepoint=PRINTABLE_END),
    min_size=1,
)


# Feature: message-cipher, Property 1: Encode-Decode Round Trip
@settings(max_examples=100)
@given(key=printable_ascii_nonempty, plaintext=printable_ascii)
def test_roundtrip(key, plaintext):
    """Encoding then decoding with the same key recovers the original plaintext.

    **Validates: Requirements 2.1, 3.1, 3.3**
    """
    assert decode(key, encode(key, plaintext)) == plaintext


# Feature: message-cipher, Property 2: Decode-Encode Round Trip
@settings(max_examples=100)
@given(key=printable_ascii_nonempty, ciphertext=printable_ascii)
def test_reverse_roundtrip(key, ciphertext):
    """Decoding then encoding with the same key recovers the original ciphertext.

    **Validates: Requirements 3.2**
    """
    assert encode(key, decode(key, ciphertext)) == ciphertext


# Feature: message-cipher, Property 3: No Positional Character Match
@settings(max_examples=100)
@given(key=printable_ascii_nonempty, plaintext=printable_ascii_nonempty)
def test_no_character_match(key, plaintext):
    """No character in ciphertext matches the plaintext character at the same position.

    **Validates: Requirements 1.1**
    """
    ciphertext = encode(key, plaintext)
    for i, (p_char, c_char) in enumerate(zip(plaintext, ciphertext)):
        assert p_char != c_char, (
            f"Character match at position {i}: '{p_char}' == '{c_char}'"
        )


# Feature: message-cipher, Property 4: Length Preservation
@settings(max_examples=100)
@given(key=printable_ascii_nonempty, plaintext=printable_ascii)
def test_length_preservation(key, plaintext):
    """Ciphertext length always equals plaintext length.

    **Validates: Requirements 1.5**
    """
    assert len(encode(key, plaintext)) == len(plaintext)


# Feature: message-cipher, Property 5: Determinism
@settings(max_examples=100)
@given(key=printable_ascii_nonempty, plaintext=printable_ascii)
def test_determinism(key, plaintext):
    """Calling encode/decode multiple times with the same inputs returns the same result.

    **Validates: Requirements 1.4, 2.5**
    """
    ciphertext1 = encode(key, plaintext)
    ciphertext2 = encode(key, plaintext)
    assert ciphertext1 == ciphertext2

    decoded1 = decode(key, ciphertext1)
    decoded2 = decode(key, ciphertext1)
    assert decoded1 == decoded2


# Feature: message-cipher, Property 6: Key Sensitivity
@settings(max_examples=100)
@given(
    keys=st.tuples(printable_ascii_nonempty, printable_ascii_nonempty).filter(
        lambda t: t[0] != t[1]
    ),
    plaintext=printable_ascii_nonempty,
)
def test_key_sensitivity(keys, plaintext):
    """Different keys produce different ciphertexts for the same plaintext,
    provided the keys differ within the first len(plaintext) characters.

    **Validates: Requirements 2.4, 4.1, 4.2**
    """
    key1, key2 = keys
    # Only test when keys produce different effective key sequences
    # (i.e., differ within the cycling range of the plaintext)
    effective_key1 = "".join(key1[i % len(key1)] for i in range(len(plaintext)))
    effective_key2 = "".join(key2[i % len(key2)] for i in range(len(plaintext)))
    assume(effective_key1 != effective_key2)
    assert encode(key1, plaintext) != encode(key2, plaintext)


# Feature: message-cipher, Property 7: Type Validation with Key Priority
@settings(max_examples=100)
@given(
    invalid_key=st.one_of(
        st.none(),
        st.integers(),
        st.lists(st.integers()),
        st.floats(),
    )
)
def test_type_validation(invalid_key):
    """TypeError is raised for invalid key regardless of text validity.

    **Validates: Requirements 5.1, 5.2, 5.3**
    """
    # Invalid key with valid text should raise TypeError for key
    with pytest.raises(TypeError, match="Key must be a string"):
        encode(invalid_key, "valid text")

    with pytest.raises(TypeError, match="Key must be a string"):
        decode(invalid_key, "valid text")

    # Invalid key with invalid text should still raise TypeError for key first
    with pytest.raises(TypeError, match="Key must be a string"):
        encode(invalid_key, 12345)

    with pytest.raises(TypeError, match="Key must be a string"):
        decode(invalid_key, 12345)


# Feature: message-cipher, Property 8: Output Always Printable ASCII
@settings(max_examples=100)
@given(key=printable_ascii_nonempty, plaintext=printable_ascii)
def test_output_printable(key, plaintext):
    """All output characters are within printable ASCII range (32-126).

    **Validates: terminal-safe output**
    """
    ciphertext = encode(key, plaintext)
    for ch in ciphertext:
        assert PRINTABLE_START <= ord(ch) <= PRINTABLE_END
