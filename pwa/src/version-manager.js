/**
 * version-manager.js — Version Management Module
 *
 * Provides functions for loading and validating the application version,
 * and fetching release notes for a given version.
 */

/**
 * Validates that a string matches MAJOR.MINOR.PATCH format
 * where each component is a non-negative integer with no leading zeros
 * (except "0" itself).
 * @param {string} version
 * @returns {boolean}
 */
export function isValidVersion(version) {
  if (typeof version !== 'string') {
    return false;
  }

  const parts = version.split('.');
  if (parts.length !== 3) {
    return false;
  }

  for (const part of parts) {
    // Must not be empty
    if (part.length === 0) {
      return false;
    }

    // Must contain only digits
    if (!/^\d+$/.test(part)) {
      return false;
    }

    // No leading zeros except for "0" itself
    if (part.length > 1 && part[0] === '0') {
      return false;
    }
  }

  return true;
}

/**
 * Loads the version string from version.json.
 * Returns "unknown" if fetch fails or format is invalid.
 * @returns {Promise<string>}
 */
export async function loadVersion() {
  try {
    const response = await fetch('version.json');
    if (!response.ok) {
      return 'unknown';
    }

    const data = await response.json();

    if (!data || !isValidVersion(data.version)) {
      return 'unknown';
    }

    return data.version;
  } catch {
    return 'unknown';
  }
}

/**
 * Loads release notes for a given version from release-notes.json.
 * Returns null if no entry exists for the version or on error.
 * @param {string} version
 * @returns {Promise<{version: string, date: string, changes: string[]} | null>}
 */
export async function loadReleaseNotes(version) {
  try {
    const response = await fetch('release-notes.json');
    if (!response.ok) {
      return null;
    }

    const data = await response.json();

    if (!data || !Array.isArray(data.releases)) {
      return null;
    }

    const entry = data.releases.find((r) => r.version === version);
    return entry || null;
  } catch {
    return null;
  }
}

/**
 * Loads all release notes entries from release-notes.json.
 * Returns an empty array on error.
 * @returns {Promise<{version: string, date: string, changes: string[]}[]>}
 */
export async function loadAllReleaseNotes() {
  try {
    const response = await fetch('release-notes.json');
    if (!response.ok) {
      return [];
    }

    const data = await response.json();

    if (!data || !Array.isArray(data.releases)) {
      return [];
    }

    return data.releases;
  } catch {
    return [];
  }
}
