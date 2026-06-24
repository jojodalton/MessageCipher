/**
 * Theme Management Module
 * Handles dark/light theme switching with localStorage persistence
 * and graceful fallback to in-memory storage when localStorage is unavailable.
 *
 * Storage key: 'messagecipher-theme'
 * Application: Sets document.documentElement.dataset.theme which triggers CSS variable switch.
 */

const STORAGE_KEY = 'messagecipher-theme';
const VALID_THEMES = ['dark', 'light'];

// In-memory fallback when localStorage is unavailable
let memoryTheme = null;

/**
 * Check if localStorage is available.
 * @returns {boolean}
 */
function isLocalStorageAvailable() {
  try {
    const testKey = '__theme_test__';
    localStorage.setItem(testKey, '1');
    localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

/**
 * Reads the persisted theme from localStorage.
 * Returns null if no valid theme is stored or localStorage is unavailable.
 * @returns {string|null} 'dark', 'light', or null
 */
export function loadPersistedTheme() {
  if (isLocalStorageAvailable()) {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (VALID_THEMES.includes(stored)) {
      return stored;
    }
    return null;
  }
  // Fallback to in-memory value
  return memoryTheme;
}

/**
 * Persists the theme mode to localStorage (or in-memory fallback).
 * @param {string} mode - 'dark' or 'light'
 */
export function persistTheme(mode) {
  if (isLocalStorageAvailable()) {
    localStorage.setItem(STORAGE_KEY, mode);
  }
  // Always update in-memory fallback
  memoryTheme = mode;
}

/**
 * Returns the current active theme based on the DOM data attribute.
 * Falls back to the in-memory value if DOM is unavailable.
 * @returns {string} 'dark' or 'light'
 */
export function getCurrentTheme() {
  if (typeof document !== 'undefined' && document.documentElement) {
    return document.documentElement.dataset.theme || memoryTheme || 'light';
  }
  return memoryTheme || 'light';
}

/**
 * Applies a theme to the DOM by setting the data-theme attribute.
 * @param {string} mode - 'dark' or 'light'
 */
function applyTheme(mode) {
  if (typeof document !== 'undefined' && document.documentElement) {
    document.documentElement.dataset.theme = mode;
  }
  memoryTheme = mode;
}

/**
 * Initializes the theme on app load.
 * 1. Checks localStorage for a persisted theme
 * 2. If not found or invalid, detects system preference via prefers-color-scheme
 * 3. Applies the resolved theme to the DOM
 * @returns {string} The applied theme mode ('dark' or 'light')
 */
export function initTheme() {
  // Step 1: Check persisted preference
  const persisted = loadPersistedTheme();
  if (persisted) {
    applyTheme(persisted);
    return persisted;
  }

  // Step 2: Fall back to system preference
  let mode = 'light';
  if (typeof window !== 'undefined' && window.matchMedia) {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    mode = prefersDark ? 'dark' : 'light';
  }

  // Step 3: Apply and return
  applyTheme(mode);
  return mode;
}

/**
 * Toggles between dark and light themes.
 * Persists the new choice and applies it to the DOM.
 * @returns {string} The new active theme mode ('dark' or 'light')
 */
export function toggleTheme() {
  const current = getCurrentTheme();
  const newMode = current === 'dark' ? 'light' : 'dark';
  persistTheme(newMode);
  applyTheme(newMode);
  return newMode;
}
