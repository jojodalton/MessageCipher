/**
 * validator.js — Input Validation Module
 *
 * Provides validation functions for key, message/ciphertext,
 * and copy eligibility checks.
 */

const PRINTABLE_START = 32;
const PRINTABLE_END = 126;
const MAX_KEY_LENGTH = 1000;

/**
 * Returns true if the given character's code point is in the
 * printable ASCII range (32–126 inclusive).
 * @param {string} ch - A single character string
 * @returns {boolean}
 */
export function isPrintableAscii(ch) {
  const code = ch.charCodeAt(0);
  return code >= PRINTABLE_START && code <= PRINTABLE_END;
}

/**
 * Validates a cipher key.
 * - Must be non-empty
 * - Must be at most 1000 characters
 * - All characters must be printable ASCII (32–126)
 *
 * @param {string} key - The key to validate
 * @returns {{ valid: boolean, error: string }}
 */
export function isValidKey(key) {
  if (key.length === 0) {
    return { valid: false, error: 'Key must not be empty' };
  }

  if (key.length > MAX_KEY_LENGTH) {
    return { valid: false, error: 'Key must be at most 1000 characters' };
  }

  const forbidden = [];
  for (let i = 0; i < key.length; i++) {
    if (!isPrintableAscii(key[i])) {
      forbidden.push(i);
    }
  }

  if (forbidden.length > 0) {
    const chars = forbidden.map(i => key[i]);
    const unique = [...new Set(chars)];
    return {
      valid: false,
      error: `Key contains forbidden characters at position(s): ${forbidden.join(', ')}`,
    };
  }

  return { valid: true, error: '' };
}

/**
 * Finds indices of characters in `text` that are outside the
 * printable ASCII range (32–126). When `allowNewline` is true,
 * newline characters (code 10) are permitted and not flagged.
 *
 * @param {string} text - The text to scan
 * @param {boolean} allowNewline - Whether to permit newline (char code 10)
 * @returns {number[]} Array of indices with invalid characters
 */
export function findForbiddenPositions(text, allowNewline) {
  const positions = [];
  for (let i = 0; i < text.length; i++) {
    const code = text.charCodeAt(i);
    if (code >= PRINTABLE_START && code <= PRINTABLE_END) {
      continue;
    }
    if (allowNewline && code === 10) {
      continue;
    }
    positions.push(i);
  }
  return positions;
}

/**
 * Returns true if the text is eligible for copying:
 * non-empty and contains at least one non-whitespace character.
 *
 * @param {string} text - The text to check
 * @returns {boolean}
 */
export function isCopyEligible(text) {
  return text.length > 0 && /\S/.test(text);
}
