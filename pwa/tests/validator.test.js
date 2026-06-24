import { describe, it, expect } from 'vitest';
import {
  isPrintableAscii,
  isValidKey,
  findForbiddenPositions,
  isCopyEligible,
} from '../src/validator.js';

describe('isPrintableAscii', () => {
  it('returns true for space (char code 32)', () => {
    expect(isPrintableAscii(' ')).toBe(true);
  });

  it('returns true for tilde (char code 126)', () => {
    expect(isPrintableAscii('~')).toBe(true);
  });

  it('returns true for regular letters and digits', () => {
    expect(isPrintableAscii('A')).toBe(true);
    expect(isPrintableAscii('z')).toBe(true);
    expect(isPrintableAscii('5')).toBe(true);
  });

  it('returns false for newline (char code 10)', () => {
    expect(isPrintableAscii('\n')).toBe(false);
  });

  it('returns false for tab (char code 9)', () => {
    expect(isPrintableAscii('\t')).toBe(false);
  });

  it('returns false for DEL (char code 127)', () => {
    expect(isPrintableAscii('\x7F')).toBe(false);
  });

  it('returns false for null (char code 0)', () => {
    expect(isPrintableAscii('\x00')).toBe(false);
  });
});

describe('isValidKey', () => {
  it('returns error for empty key', () => {
    const result = isValidKey('');
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Key must not be empty');
  });

  it('returns valid for single character key', () => {
    const result = isValidKey('a');
    expect(result.valid).toBe(true);
    expect(result.error).toBe('');
  });

  it('returns valid for key of exactly 1000 characters', () => {
    const key = 'a'.repeat(1000);
    const result = isValidKey(key);
    expect(result.valid).toBe(true);
    expect(result.error).toBe('');
  });

  it('returns error for key of 1001 characters', () => {
    const key = 'a'.repeat(1001);
    const result = isValidKey(key);
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Key must be at most 1000 characters');
  });

  it('returns error for key with non-printable characters', () => {
    const result = isValidKey('hello\x01world');
    expect(result.valid).toBe(false);
    expect(result.error).toContain('forbidden');
  });

  it('returns valid for all printable ASCII characters', () => {
    let key = '';
    for (let i = 32; i <= 126; i++) {
      key += String.fromCharCode(i);
    }
    const result = isValidKey(key);
    expect(result.valid).toBe(true);
    expect(result.error).toBe('');
  });
});

describe('findForbiddenPositions', () => {
  it('returns empty array for valid printable ASCII text', () => {
    expect(findForbiddenPositions('Hello, world!', false)).toEqual([]);
  });

  it('returns positions of non-printable characters', () => {
    expect(findForbiddenPositions('A\x01B\x02C', false)).toEqual([1, 3]);
  });

  it('flags newlines when allowNewline is false', () => {
    expect(findForbiddenPositions('line1\nline2', false)).toEqual([5]);
  });

  it('permits newlines when allowNewline is true', () => {
    expect(findForbiddenPositions('line1\nline2', true)).toEqual([]);
  });

  it('still flags other control chars when allowNewline is true', () => {
    expect(findForbiddenPositions('A\tB\nC\x00D', true)).toEqual([1, 5]);
  });

  it('returns empty array for empty string', () => {
    expect(findForbiddenPositions('', false)).toEqual([]);
    expect(findForbiddenPositions('', true)).toEqual([]);
  });
});

describe('isCopyEligible', () => {
  it('returns false for empty string', () => {
    expect(isCopyEligible('')).toBe(false);
  });

  it('returns false for whitespace-only string', () => {
    expect(isCopyEligible('   ')).toBe(false);
    expect(isCopyEligible('\t\n ')).toBe(false);
  });

  it('returns true for non-empty string with non-whitespace chars', () => {
    expect(isCopyEligible('hello')).toBe(true);
    expect(isCopyEligible(' x ')).toBe(true);
  });

  it('returns true for string with leading/trailing whitespace', () => {
    expect(isCopyEligible('  text  ')).toBe(true);
  });
});
