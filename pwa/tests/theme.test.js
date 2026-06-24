import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  loadPersistedTheme,
  persistTheme,
  getCurrentTheme,
  initTheme,
  toggleTheme,
} from '../src/theme.js';

describe('theme.js', () => {
  let localStorageMock;

  beforeEach(() => {
    // Mock localStorage
    localStorageMock = (() => {
      let store = {};
      return {
        getItem: vi.fn((key) => store[key] ?? null),
        setItem: vi.fn((key, val) => { store[key] = String(val); }),
        removeItem: vi.fn((key) => { delete store[key]; }),
        clear: () => { store = {}; },
      };
    })();

    Object.defineProperty(globalThis, 'localStorage', {
      value: localStorageMock,
      writable: true,
      configurable: true,
    });

    // Mock document.documentElement
    if (typeof document === 'undefined') {
      globalThis.document = {
        documentElement: { dataset: {} },
      };
    } else {
      document.documentElement.dataset.theme = '';
    }

    // Mock window.matchMedia
    globalThis.window = globalThis.window || {};
    globalThis.window.matchMedia = vi.fn((query) => ({
      matches: false,
      media: query,
    }));
  });

  afterEach(() => {
    // Clean up dataset
    if (document && document.documentElement) {
      delete document.documentElement.dataset.theme;
    }
  });

  describe('loadPersistedTheme', () => {
    it('returns null when no theme is stored', () => {
      expect(loadPersistedTheme()).toBe(null);
    });

    it('returns "dark" when dark is stored', () => {
      localStorageMock.setItem('messagecipher-theme', 'dark');
      expect(loadPersistedTheme()).toBe('dark');
    });

    it('returns "light" when light is stored', () => {
      localStorageMock.setItem('messagecipher-theme', 'light');
      expect(loadPersistedTheme()).toBe('light');
    });

    it('returns null for invalid stored values', () => {
      localStorageMock.setItem('messagecipher-theme', 'invalid');
      expect(loadPersistedTheme()).toBe(null);
    });
  });

  describe('persistTheme', () => {
    it('stores dark theme in localStorage', () => {
      persistTheme('dark');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('messagecipher-theme', 'dark');
    });

    it('stores light theme in localStorage', () => {
      persistTheme('light');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('messagecipher-theme', 'light');
    });
  });

  describe('getCurrentTheme', () => {
    it('returns theme from DOM data attribute', () => {
      document.documentElement.dataset.theme = 'dark';
      expect(getCurrentTheme()).toBe('dark');
    });

    it('defaults to light when no theme is set', () => {
      document.documentElement.dataset.theme = '';
      expect(getCurrentTheme()).toBe('light');
    });
  });

  describe('initTheme', () => {
    it('applies persisted theme from localStorage', () => {
      localStorageMock.setItem('messagecipher-theme', 'dark');
      const result = initTheme();
      expect(result).toBe('dark');
      expect(document.documentElement.dataset.theme).toBe('dark');
    });

    it('falls back to system preference when nothing persisted', () => {
      globalThis.window.matchMedia = vi.fn(() => ({ matches: true }));
      const result = initTheme();
      expect(result).toBe('dark');
      expect(document.documentElement.dataset.theme).toBe('dark');
    });

    it('defaults to light when system prefers light', () => {
      globalThis.window.matchMedia = vi.fn(() => ({ matches: false }));
      const result = initTheme();
      expect(result).toBe('light');
      expect(document.documentElement.dataset.theme).toBe('light');
    });
  });

  describe('toggleTheme', () => {
    it('switches from light to dark', () => {
      document.documentElement.dataset.theme = 'light';
      const result = toggleTheme();
      expect(result).toBe('dark');
      expect(document.documentElement.dataset.theme).toBe('dark');
    });

    it('switches from dark to light', () => {
      document.documentElement.dataset.theme = 'dark';
      const result = toggleTheme();
      expect(result).toBe('light');
      expect(document.documentElement.dataset.theme).toBe('light');
    });

    it('persists the new theme', () => {
      document.documentElement.dataset.theme = 'light';
      toggleTheme();
      expect(localStorageMock.setItem).toHaveBeenCalledWith('messagecipher-theme', 'dark');
    });
  });

  describe('localStorage unavailability (graceful fallback)', () => {
    beforeEach(() => {
      // Make localStorage throw on access
      Object.defineProperty(globalThis, 'localStorage', {
        get() { throw new Error('localStorage is not available'); },
        configurable: true,
      });
    });

    it('toggleTheme still works in-memory', () => {
      document.documentElement.dataset.theme = 'light';
      const result = toggleTheme();
      expect(result).toBe('dark');
      expect(document.documentElement.dataset.theme).toBe('dark');
    });

    it('toggle round-trips correctly without localStorage', () => {
      document.documentElement.dataset.theme = 'dark';
      const r1 = toggleTheme();
      expect(r1).toBe('light');
      const r2 = toggleTheme();
      expect(r2).toBe('dark');
    });

    it('getCurrentTheme returns value from DOM', () => {
      document.documentElement.dataset.theme = 'dark';
      expect(getCurrentTheme()).toBe('dark');
    });
  });
});
