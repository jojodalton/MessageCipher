/**
 * Clipboard Integration Module
 * Provides copy/paste functionality using the browser Clipboard API
 * with graceful error handling for unavailable or denied access.
 */

/**
 * Checks whether the Clipboard API is available in the current browser context.
 * @returns {boolean} true if navigator.clipboard exists
 */
export function isClipboardAvailable() {
  return !!(typeof navigator !== 'undefined' && navigator.clipboard);
}

/**
 * Copies the given text to the device clipboard.
 * @param {string} text - The text to copy
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function copyToClipboard(text) {
  if (!isClipboardAvailable()) {
    return { success: false, error: 'Clipboard API not available. Use system paste gesture.' };
  }

  try {
    await navigator.clipboard.writeText(text);
    return { success: true };
  } catch (err) {
    if (err.name === 'NotAllowedError') {
      return { success: false, error: 'Clipboard permission denied. Use system paste gesture.' };
    }
    return { success: false, error: 'Clipboard API not available. Use system paste gesture.' };
  }
}

/**
 * Reads text from the device clipboard.
 * @returns {Promise<{success: boolean, text?: string, error?: string}>}
 */
export async function pasteFromClipboard() {
  if (!isClipboardAvailable()) {
    return { success: false, error: 'Clipboard API not available. Use system paste gesture.' };
  }

  try {
    const text = await navigator.clipboard.readText();
    return { success: true, text };
  } catch (err) {
    if (err.name === 'NotAllowedError') {
      return { success: false, error: 'Clipboard permission denied. Use system paste gesture.' };
    }
    return { success: false, error: 'Clipboard API not available. Use system paste gesture.' };
  }
}
