/**
 * Cipher engine module implementing a modified Vigenère cipher over printable ASCII.
 * Port of the Python message_cipher.py to JavaScript ES module.
 */

const PRINTABLE_START = 32;
const PRINTABLE_END = 126;
const PRINTABLE_RANGE = 95; // PRINTABLE_END - PRINTABLE_START + 1

/**
 * Encode a single line by applying the shift formula with key cycling.
 * Key position resets at the start of each line.
 *
 * Formula per character:
 *   ((charCode - 32) + ((keyCharCode - 32) % 94 + 1)) % 95 + 32
 *
 * @param {string} key - Non-empty printable ASCII key.
 * @param {string} line - A single line of printable ASCII text (no newlines).
 * @returns {string} The encoded line.
 */
export function encodeLine(key, line) {
  const keyLen = key.length;
  let result = '';
  for (let i = 0; i < line.length; i++) {
    const charCode = line.charCodeAt(i);
    const keyCharCode = key.charCodeAt(i % keyLen);
    const shift = (keyCharCode - PRINTABLE_START) % (PRINTABLE_RANGE - 1) + 1;
    const shifted = (charCode - PRINTABLE_START + shift) % PRINTABLE_RANGE + PRINTABLE_START;
    result += String.fromCharCode(shifted);
  }
  return result;
}

/**
 * Decode a single line by applying the inverse shift formula with key cycling.
 * Key position resets at the start of each line.
 *
 * Formula per character:
 *   ((charCode - 32) - ((keyCharCode - 32) % 94 + 1) + 95) % 95 + 32
 *
 * @param {string} key - Non-empty printable ASCII key.
 * @param {string} line - A single line of encoded printable ASCII text (no newlines).
 * @returns {string} The decoded line.
 */
export function decodeLine(key, line) {
  const keyLen = key.length;
  let result = '';
  for (let i = 0; i < line.length; i++) {
    const charCode = line.charCodeAt(i);
    const keyCharCode = key.charCodeAt(i % keyLen);
    const shift = (keyCharCode - PRINTABLE_START) % (PRINTABLE_RANGE - 1) + 1;
    const shifted = (charCode - PRINTABLE_START - shift + PRINTABLE_RANGE) % PRINTABLE_RANGE + PRINTABLE_START;
    result += String.fromCharCode(shifted);
  }
  return result;
}

/**
 * Encode a message that may contain newlines.
 * Splits on '\n', encodes each line independently (resetting key position),
 * and rejoins with '\n'.
 *
 * @param {string} key - Non-empty printable ASCII key.
 * @param {string} message - Printable ASCII message (newlines allowed).
 * @returns {string} The encoded message.
 */
export function encode(key, message) {
  if (message === '') return '';
  const lines = message.split('\n');
  return lines.map(line => encodeLine(key, line)).join('\n');
}

/**
 * Decode a ciphertext that may contain newlines.
 * Splits on '\n', decodes each line independently (resetting key position),
 * and rejoins with '\n'.
 *
 * @param {string} key - Non-empty printable ASCII key.
 * @param {string} ciphertext - Printable ASCII ciphertext (newlines allowed).
 * @returns {string} The decoded message.
 */
export function decode(key, ciphertext) {
  if (ciphertext === '') return '';
  const lines = ciphertext.split('\n');
  return lines.map(line => decodeLine(key, line)).join('\n');
}
