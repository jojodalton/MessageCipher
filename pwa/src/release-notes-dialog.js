/**
 * release-notes-dialog.js — Release Notes Dialog Module
 *
 * Provides functions for showing and closing a modal dialog
 * that displays release notes for the current application version.
 * Supports keyboard (Escape) and click-outside-to-dismiss behavior,
 * and manages focus return to the trigger element.
 */

/** @type {HTMLElement | null} */
let dialogOverlay = null;

/** @type {HTMLElement | null} */
let triggerEl = null;

/** @type {((e: KeyboardEvent) => void) | null} */
let keydownHandler = null;

/**
 * Creates and shows the release notes modal dialog.
 * Accepts either a single entry or an array of all releases.
 * If entries is null/empty, a fallback message is displayed.
 *
 * @param {{ version: string, date: string, changes: string[] }[] | { version: string, date: string, changes: string[] } | null} entries
 * @param {HTMLElement} triggerElement - Element to return focus to on close
 */
export function showReleaseNotesDialog(entries, triggerElement) {
  // Close any existing dialog first
  if (dialogOverlay) {
    closeReleaseNotesDialog();
  }

  triggerEl = triggerElement;

  // Normalize: if a single entry is passed, wrap it in an array
  let releases = entries;
  if (entries && !Array.isArray(entries)) {
    releases = [entries];
  }

  // Create the backdrop overlay
  dialogOverlay = document.createElement('div');
  dialogOverlay.className = 'release-notes-overlay';
  dialogOverlay.addEventListener('click', handleOverlayClick);

  // Create the dialog panel
  const dialog = document.createElement('div');
  dialog.setAttribute('role', 'dialog');
  dialog.setAttribute('aria-modal', 'true');
  dialog.setAttribute('aria-labelledby', 'release-notes-heading');
  dialog.className = 'release-notes-dialog';

  // Build dialog content
  dialog.innerHTML = buildDialogContent(releases);

  dialogOverlay.appendChild(dialog);
  document.body.appendChild(dialogOverlay);

  // Attach Escape key handler
  keydownHandler = handleKeydown;
  document.addEventListener('keydown', keydownHandler);

  // Focus the close button for accessibility
  const closeBtn = dialog.querySelector('.release-notes-close');
  if (closeBtn) {
    closeBtn.focus();
  }
}

/**
 * Closes the release notes dialog and returns focus to the trigger element.
 */
export function closeReleaseNotesDialog() {
  if (keydownHandler) {
    document.removeEventListener('keydown', keydownHandler);
    keydownHandler = null;
  }

  if (dialogOverlay) {
    dialogOverlay.removeEventListener('click', handleOverlayClick);
    dialogOverlay.remove();
    dialogOverlay = null;
  }

  if (triggerEl) {
    triggerEl.focus();
    triggerEl = null;
  }
}

/**
 * Builds the inner HTML content for the dialog.
 * Shows all releases, or a fallback message when no entries are available.
 *
 * @param {{ version: string, date: string, changes: string[] }[] | null} releases
 * @returns {string}
 */
function buildDialogContent(releases) {
  const closeButton = '<button class="release-notes-close" aria-label="Close release notes">&times;</button>';

  if (!releases || !Array.isArray(releases) || releases.length === 0) {
    return `
      <h2 id="release-notes-heading">Release Notes</h2>
      ${closeButton}
      <p class="release-notes-fallback">No release notes available for this version</p>
    `;
  }

  let html = `
    <h2 id="release-notes-heading">Release Notes</h2>
    ${closeButton}
  `;

  for (const entry of releases) {
    if (!entry || !Array.isArray(entry.changes) || entry.changes.length === 0) continue;

    const version = escapeHTML(entry.version);
    const date = escapeHTML(entry.date);
    const changeItems = entry.changes
      .map((change) => `<li>${escapeHTML(change)}</li>`)
      .join('');

    html += `
      <section class="release-entry">
        <h3>v${version} <span class="release-notes-date">— ${date}</span></h3>
        <ul class="release-notes-changes">${changeItems}</ul>
      </section>
    `;
  }

  return html;
}

/**
 * Handles keydown events on the document to close on Escape.
 * @param {KeyboardEvent} e
 */
function handleKeydown(e) {
  if (e.key === 'Escape') {
    closeReleaseNotesDialog();
  }
}

/**
 * Handles click on the overlay backdrop.
 * Closes the dialog if the click target is the overlay itself
 * (not the dialog panel content).
 * Also handles the close button click.
 * @param {MouseEvent} e
 */
function handleOverlayClick(e) {
  // Close button click
  if (e.target.classList.contains('release-notes-close')) {
    closeReleaseNotesDialog();
    return;
  }

  // Click outside the dialog (on the overlay backdrop)
  if (e.target === dialogOverlay) {
    closeReleaseNotesDialog();
  }
}

/**
 * Escapes HTML special characters to prevent XSS.
 * @param {string} str
 * @returns {string}
 */
function escapeHTML(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
