/**
 * ui.js — DOM Manipulation Module
 *
 * Provides functions for rendering status messages, reading/writing
 * form field values, clearing fields, and updating copy button states.
 * Status messages are rendered inside an aria-live region for
 * screen reader announcement.
 */

/**
 * Displays a status message in the live region with appropriate styling.
 * The type controls the visual appearance (success = green, error = red).
 *
 * @param {string} message - The status message to display
 * @param {'success' | 'error'} type - The message type for styling
 */
export function showStatus(message, type) {
  const banner = document.getElementById('status-banner');
  if (!banner) return;

  banner.textContent = message;
  banner.className = `status-banner status-${type}`;
  banner.hidden = false;
}

/**
 * Clears the status region, removing any displayed message.
 */
export function clearStatus() {
  const banner = document.getElementById('status-banner');
  if (!banner) return;

  banner.textContent = '';
  banner.className = 'status-banner';
  banner.hidden = true;
}

/**
 * Empties the key input, message textarea, ciphertext textarea,
 * and clears the status banner.
 */
export function clearAllFields() {
  const keyInput = document.getElementById('key-input');
  const messageTextarea = document.getElementById('message-textarea');
  const ciphertextTextarea = document.getElementById('ciphertext-textarea');

  if (keyInput) keyInput.value = '';
  if (messageTextarea) {
    messageTextarea.value = '';
    messageTextarea.dispatchEvent(new Event('input', { bubbles: true }));
  }
  if (ciphertextTextarea) {
    ciphertextTextarea.value = '';
    ciphertextTextarea.dispatchEvent(new Event('input', { bubbles: true }));
  }

  clearStatus();
}

/**
 * Returns the current value of the key input field.
 * @returns {string}
 */
export function getKeyValue() {
  const keyInput = document.getElementById('key-input');
  return keyInput ? keyInput.value : '';
}

/**
 * Returns the current value of the message textarea.
 * @returns {string}
 */
export function getMessageValue() {
  const messageTextarea = document.getElementById('message-textarea');
  return messageTextarea ? messageTextarea.value : '';
}

/**
 * Returns the current value of the ciphertext textarea.
 * @returns {string}
 */
export function getCiphertextValue() {
  const ciphertextTextarea = document.getElementById('ciphertext-textarea');
  return ciphertextTextarea ? ciphertextTextarea.value : '';
}

/**
 * Sets the value of the message textarea.
 * @param {string} text - The text to set
 */
export function setMessageValue(text) {
  const messageTextarea = document.getElementById('message-textarea');
  if (messageTextarea) messageTextarea.value = text;
}

/**
 * Sets the value of the ciphertext textarea.
 * @param {string} text - The text to set
 */
export function setCiphertextValue(text) {
  const ciphertextTextarea = document.getElementById('ciphertext-textarea');
  if (ciphertextTextarea) ciphertextTextarea.value = text;
}

/**
 * Updates a copy button's disabled state based on the content of
 * its associated textarea. The button is disabled when the textarea
 * is empty or contains only whitespace.
 *
 * @param {HTMLTextAreaElement} textarea - The textarea to check
 * @param {HTMLButtonElement} button - The copy button to enable/disable
 */
export function updateCopyButtonState(textarea, button) {
  if (!textarea || !button) return;

  const text = textarea.value;
  const hasContent = text.length > 0 && /\S/.test(text);
  button.disabled = !hasContent;
}
