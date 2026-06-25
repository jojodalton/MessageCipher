/**
 * app.js — Main Application Entry Point
 *
 * Wires together the cipher, validator, clipboard, theme, and ui modules.
 * Registers event listeners for all user interactions and handles
 * the encode, decode, clear, copy, paste, and theme toggle flows.
 * Registers the service worker for offline support.
 */

import { encode, decode } from './cipher.js';
import { isValidKey, findForbiddenPositions, isCopyEligible } from './validator.js';
import { copyToClipboard, pasteFromClipboard } from './clipboard.js';
import { initTheme, toggleTheme } from './theme.js';
import {
  showStatus,
  clearStatus,
  clearAllFields,
  getKeyValue,
  getMessageValue,
  getCiphertextValue,
  setMessageValue,
  setCiphertextValue,
  updateCopyButtonState,
} from './ui.js';
import { loadVersion, loadReleaseNotes } from './version-manager.js';
import { showReleaseNotesDialog } from './release-notes-dialog.js';
import { initHighlight } from './highlight-engine.js';

/**
 * Handles the Encode button click.
 * Validates key and message, then encodes and displays ciphertext.
 */
function handleEncode() {
  clearStatus();

  const key = getKeyValue();
  const keyResult = isValidKey(key);
  if (!keyResult.valid) {
    showStatus(keyResult.error, 'error');
    return;
  }

  const message = getMessageValue();
  const forbidden = findForbiddenPositions(message, true);
  if (forbidden.length > 0) {
    showStatus('Message contains invalid characters', 'error');
    return;
  }

  const ciphertext = encode(key, message);
  setCiphertextValue(ciphertext);
  updateCiphertextCopyState();
  showStatus('Encoded successfully', 'success');
}

/**
 * Handles the Decode button click.
 * Validates key and ciphertext, then decodes and displays message.
 */
function handleDecode() {
  clearStatus();

  const key = getKeyValue();
  const keyResult = isValidKey(key);
  if (!keyResult.valid) {
    showStatus(keyResult.error, 'error');
    return;
  }

  const ciphertext = getCiphertextValue();
  const forbidden = findForbiddenPositions(ciphertext, true);
  if (forbidden.length > 0) {
    showStatus('Ciphertext contains invalid characters', 'error');
    return;
  }

  const message = decode(key, ciphertext);
  setMessageValue(message);
  updateMessageCopyState();
  showStatus('Decoded successfully', 'success');
}

/**
 * Handles the Clear button click.
 * Clears all fields and resets copy button states.
 */
function handleClear() {
  clearAllFields();
  updateMessageCopyState();
  updateCiphertextCopyState();
}

/**
 * Handles a copy button click for the given textarea.
 * @param {'message' | 'ciphertext'} target - Which textarea to copy from
 */
async function handleCopy(target) {
  const text = target === 'message' ? getMessageValue() : getCiphertextValue();

  if (!isCopyEligible(text)) {
    return;
  }

  const result = await copyToClipboard(text);
  if (result.success) {
    showStatus('Copied to clipboard', 'success');
  } else {
    showStatus(result.error, 'error');
  }
}

/**
 * Handles a paste button click for the given textarea.
 * @param {'message' | 'ciphertext'} target - Which textarea to paste into
 */
async function handlePaste(target) {
  const result = await pasteFromClipboard();
  if (result.success) {
    if (target === 'message') {
      setMessageValue(result.text);
      updateMessageCopyState();
    } else {
      setCiphertextValue(result.text);
      updateCiphertextCopyState();
    }
  } else {
    showStatus(result.error, 'error');
  }
}

/**
 * Updates the message copy button's disabled state.
 */
function updateMessageCopyState() {
  const textarea = document.getElementById('message-textarea');
  const button = document.getElementById('message-copy');
  updateCopyButtonState(textarea, button);
}

/**
 * Updates the ciphertext copy button's disabled state.
 */
function updateCiphertextCopyState() {
  const textarea = document.getElementById('ciphertext-textarea');
  const button = document.getElementById('ciphertext-copy');
  updateCopyButtonState(textarea, button);
}

/**
 * Initializes the version badge in the header.
 * Loads the version string and displays it. If the version is valid
 * (not "unknown"), attaches a click handler to show release notes.
 */
async function initVersionBadge() {
  const badge = document.getElementById('version-badge');
  if (!badge) return;

  const version = await loadVersion();
  badge.textContent = `v${version}`;

  if (version !== 'unknown') {
    badge.classList.add('clickable');
    badge.setAttribute('role', 'button');
    badge.setAttribute('tabindex', '0');
    badge.setAttribute('aria-label', `Version ${version}. Click to view release notes.`);

    const openReleaseNotes = async () => {
      const entry = await loadReleaseNotes(version);
      showReleaseNotesDialog(entry, badge);
    };

    badge.addEventListener('click', openReleaseNotes);
    badge.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openReleaseNotes();
      }
    });
  } else {
    badge.setAttribute('aria-label', 'Version unknown');
  }
}

/**
 * Registers the service worker for offline support.
 * Listens for controller changes and messages from the service worker
 * to notify the user when a new version is available.
 * Fails gracefully — app still functions without offline support.
 */
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    // Listen for controller changes (new service worker took over)
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      showStatus('New version available. Refresh to update.', 'success');
    });

    // Listen for messages from the service worker (SW_UPDATED notification)
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'SW_UPDATED') {
        showStatus('New version available. Refresh to update.', 'success');
      }
    });

    navigator.serviceWorker
      .register('./service-worker.js')
      .then((registration) => {
        // Listen for updates via the registration's updatefound event
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'activated') {
                showStatus('New version available. Refresh to update.', 'success');
              }
            });
          }
        });
      })
      .catch(() => {
        // Service worker registration failed — app still works online
      });
  }
}

/**
 * Initializes the application on DOMContentLoaded.
 * Sets up theme, registers event listeners, and registers service worker.
 */
function init() {
  // Initialize theme
  initTheme();

  // Action buttons
  const encodeBtn = document.getElementById('encode-btn');
  const decodeBtn = document.getElementById('decode-btn');
  const clearBtn = document.getElementById('clear-btn');

  if (encodeBtn) encodeBtn.addEventListener('click', handleEncode);
  if (decodeBtn) decodeBtn.addEventListener('click', handleDecode);
  if (clearBtn) clearBtn.addEventListener('click', handleClear);

  // Theme toggle
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) themeToggle.addEventListener('click', toggleTheme);

  // Copy buttons
  const messageCopy = document.getElementById('message-copy');
  const ciphertextCopy = document.getElementById('ciphertext-copy');

  if (messageCopy) messageCopy.addEventListener('click', () => handleCopy('message'));
  if (ciphertextCopy) ciphertextCopy.addEventListener('click', () => handleCopy('ciphertext'));

  // Paste buttons
  const messagePaste = document.getElementById('message-paste');
  const ciphertextPaste = document.getElementById('ciphertext-paste');

  if (messagePaste) messagePaste.addEventListener('click', () => handlePaste('message'));
  if (ciphertextPaste) ciphertextPaste.addEventListener('click', () => handlePaste('ciphertext'));

  // Update copy button states on textarea input
  const messageTextarea = document.getElementById('message-textarea');
  const ciphertextTextarea = document.getElementById('ciphertext-textarea');

  if (messageTextarea) {
    messageTextarea.addEventListener('input', updateMessageCopyState);
    initHighlight(messageTextarea, true);
  }
  if (ciphertextTextarea) {
    ciphertextTextarea.addEventListener('input', updateCiphertextCopyState);
    initHighlight(ciphertextTextarea, true);
  }

  // Initialize copy button states
  updateMessageCopyState();
  updateCiphertextCopyState();

  // Key visibility toggle
  const keyInput = document.getElementById('key-input');
  const keyToggle = document.getElementById('key-toggle');
  if (keyToggle && keyInput) {
    keyToggle.addEventListener('click', () => {
      if (keyInput.type === 'password') {
        keyInput.type = 'text';
        keyToggle.textContent = '🙈';
        keyToggle.setAttribute('aria-label', 'Hide key');
      } else {
        keyInput.type = 'password';
        keyToggle.textContent = '👁';
        keyToggle.setAttribute('aria-label', 'Show key');
      }
    });
  }

  // Register service worker
  registerServiceWorker();

  // Initialize version badge
  initVersionBadge();
}

document.addEventListener('DOMContentLoaded', init);
