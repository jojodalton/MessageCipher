/**
 * highlight-engine.js — Forbidden Character Highlight Engine
 *
 * Provides a real-time highlight overlay rendered behind each textarea
 * that visually marks forbidden characters as the user types, paired
 * with a count-based warning indicator.
 */

import { findForbiddenPositions } from './validator.js';

/**
 * HTML-escapes a single character.
 * @param {string} ch
 * @returns {string}
 */
function escapeChar(ch) {
  switch (ch) {
    case '&': return '&amp;';
    case '<': return '&lt;';
    case '>': return '&gt;';
    case '"': return '&quot;';
    case "'": return '&#x27;';
    default: return ch;
  }
}

/**
 * Builds the overlay innerHTML from text content.
 * All text is HTML-escaped to prevent XSS. Characters at forbidden
 * positions are wrapped in <mark> highlight spans.
 *
 * @param {string} text - The textarea content
 * @param {number[]} forbiddenPositions - Indices of forbidden chars
 * @returns {string} HTML string for the overlay
 */
export function buildOverlayHTML(text, forbiddenPositions) {
  if (text.length === 0) return '';

  const forbiddenSet = new Set(forbiddenPositions);
  let html = '';

  for (let i = 0; i < text.length; i++) {
    const escaped = escapeChar(text[i]);
    if (forbiddenSet.has(i)) {
      html += '<mark>' + escaped + '</mark>';
    } else {
      html += escaped;
    }
  }

  return html;
}

/**
 * CSS properties to copy from the textarea to the overlay
 * so that character positions align precisely.
 */
const SYNC_PROPERTIES = [
  'fontFamily',
  'fontSize',
  'lineHeight',
  'padding',
  'paddingTop',
  'paddingRight',
  'paddingBottom',
  'paddingLeft',
  'borderWidth',
  'borderTopWidth',
  'borderRightWidth',
  'borderBottomWidth',
  'borderLeftWidth',
  'boxSizing',
  'wordWrap',
  'whiteSpace',
  'overflowWrap',
];

/**
 * Copies computed CSS properties from the textarea to the overlay.
 * @param {HTMLTextAreaElement} textarea
 * @param {HTMLDivElement} overlay
 */
function syncStyles(textarea, overlay) {
  const computed = window.getComputedStyle(textarea);
  for (const prop of SYNC_PROPERTIES) {
    overlay.style[prop] = computed[prop];
  }
  // Match dimensions
  overlay.style.width = textarea.offsetWidth + 'px';
  overlay.style.height = textarea.offsetHeight + 'px';
}

/**
 * Initializes the highlight overlay for a textarea.
 * Creates the overlay div, positions it behind the textarea,
 * and attaches input/scroll/resize listeners.
 *
 * @param {HTMLTextAreaElement} textarea - The textarea to overlay
 * @param {boolean} allowNewline - Whether newlines are permitted
 * @returns {HighlightInstance}
 */
export function initHighlight(textarea, allowNewline) {
  // Create overlay div
  const overlay = document.createElement('div');
  overlay.className = 'highlight-overlay';
  overlay.setAttribute('aria-hidden', 'true');

  // Position overlay behind textarea
  overlay.style.position = 'absolute';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.pointerEvents = 'none';
  overlay.style.zIndex = '0';
  overlay.style.overflow = 'hidden';
  overlay.style.whiteSpace = 'pre-wrap';
  overlay.style.wordWrap = 'break-word';

  // Sync styles from textarea
  syncStyles(textarea, overlay);

  // Insert overlay before textarea in the same parent
  textarea.parentNode.insertBefore(overlay, textarea);

  // Ensure textarea is positioned above overlay
  const textareaPosition = window.getComputedStyle(textarea).position;
  if (textareaPosition === 'static') {
    textarea.style.position = 'relative';
  }
  textarea.style.zIndex = '1';
  textarea.style.background = 'transparent';

  // Create warning indicator element
  const warningEl = document.createElement('div');
  warningEl.className = 'highlight-warning';
  warningEl.setAttribute('aria-live', 'polite');
  warningEl.style.display = 'none';

  // Insert warning after textarea
  textarea.parentNode.insertBefore(warningEl, textarea.nextSibling);

  // Build instance
  const instance = {
    textarea,
    overlay,
    warningEl,
    allowNewline,
    listeners: [],
  };

  // Input handler — update highlight on text changes
  const inputHandler = () => {
    updateHighlight(instance);
  };

  // Scroll handler — sync overlay scroll position
  let scrollRafId = null;
  const scrollHandler = () => {
    if (scrollRafId) return;
    scrollRafId = requestAnimationFrame(() => {
      overlay.scrollTop = textarea.scrollTop;
      overlay.scrollLeft = textarea.scrollLeft;
      scrollRafId = null;
    });
  };

  // Resize handler — sync overlay dimensions
  let resizeRafId = null;
  const resizeObserver = new ResizeObserver(() => {
    if (resizeRafId) return;
    resizeRafId = requestAnimationFrame(() => {
      overlay.style.width = textarea.offsetWidth + 'px';
      overlay.style.height = textarea.offsetHeight + 'px';
      resizeRafId = null;
    });
  });
  resizeObserver.observe(textarea);

  // Attach listeners
  textarea.addEventListener('input', inputHandler);
  textarea.addEventListener('scroll', scrollHandler);

  instance.listeners.push({ event: 'input', handler: inputHandler });
  instance.listeners.push({ event: 'scroll', handler: scrollHandler });
  // Store resize observer for cleanup
  instance._resizeObserver = resizeObserver;
  instance._scrollRafId = scrollRafId;
  instance._resizeRafId = resizeRafId;

  // Initial render
  updateHighlight(instance);

  return instance;
}

/**
 * Updates the overlay content to reflect current textarea text.
 * Wraps forbidden characters in <mark> spans and updates the
 * warning indicator count.
 *
 * @param {HighlightInstance} instance
 */
export function updateHighlight(instance) {
  const { textarea, overlay, warningEl, allowNewline } = instance;
  const text = textarea.value;

  // Find forbidden positions
  const positions = findForbiddenPositions(text, allowNewline);

  // Build and set overlay HTML
  overlay.innerHTML = buildOverlayHTML(text, positions);

  // Sync scroll position
  overlay.scrollTop = textarea.scrollTop;
  overlay.scrollLeft = textarea.scrollLeft;

  // Update warning indicator
  if (positions.length > 0) {
    const label = positions.length === 1
      ? '1 invalid character'
      : `${positions.length} invalid characters`;
    warningEl.textContent = label;
    warningEl.style.display = '';
  } else {
    warningEl.textContent = '';
    warningEl.style.display = 'none';
  }
}

/**
 * Removes the overlay and detaches all listeners.
 *
 * @param {HighlightInstance} instance
 */
export function destroyHighlight(instance) {
  const { textarea, overlay, warningEl, listeners } = instance;

  // Remove event listeners
  for (const { event, handler } of listeners) {
    textarea.removeEventListener(event, handler);
  }

  // Disconnect resize observer
  if (instance._resizeObserver) {
    instance._resizeObserver.disconnect();
  }

  // Remove DOM elements
  if (overlay.parentNode) {
    overlay.parentNode.removeChild(overlay);
  }
  if (warningEl.parentNode) {
    warningEl.parentNode.removeChild(warningEl);
  }

  // Clear references
  instance.listeners = [];
  instance._resizeObserver = null;
}
