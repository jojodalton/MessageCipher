import { describe, it, expect } from 'vitest';
import { encode, decode, encodeLine, decodeLine } from '../src/cipher.js';

describe('cipher.js', () => {
  describe('encodeLine', () => {
    it('should encode a single character with a single-char key', () => {
      // key='A' (code 65), char='A' (code 65)
      // shift = (65-32) % 94 + 1 = 33 % 94 + 1 = 34
      // shifted = (65-32 + 34) % 95 + 32 = (33 + 34) % 95 + 32 = 67 % 95 + 32 = 67 + 32 = 99 → 'c'
      const result = encodeLine('A', 'A');
      expect(result).toBe('c');
    });

    it('should cycle the key across the message', () => {
      const key = 'AB';
      const msg = 'AAAA';
      const encoded = encodeLine(key, msg);
      // Position 0: key='A', char='A' → shift=34, result = (33+34)%95+32 = 99 → 'c'
      // Position 1: key='B', char='A' → shift = (66-32)%94+1 = 34%94+1 = 35, result = (33+35)%95+32 = 100 → 'd'
      // Position 2: key='A', char='A' → same as pos 0 → 'c'
      // Position 3: key='B', char='A' → same as pos 1 → 'd'
      expect(encoded).toBe('cdcd');
    });

    it('should handle space character (code 32)', () => {
      // key=' ' (code 32), char=' ' (code 32)
      // shift = (32-32) % 94 + 1 = 0 % 94 + 1 = 1
      // shifted = (32-32 + 1) % 95 + 32 = 1 % 95 + 32 = 33 → '!'
      const result = encodeLine(' ', ' ');
      expect(result).toBe('!');
    });

    it('should handle empty line', () => {
      expect(encodeLine('key', '')).toBe('');
    });
  });

  describe('decodeLine', () => {
    it('should decode a single character with a single-char key', () => {
      const result = decodeLine('A', 'c');
      expect(result).toBe('A');
    });

    it('should be inverse of encodeLine', () => {
      const key = 'TestKey';
      const msg = 'Hello, World!';
      const encoded = encodeLine(key, msg);
      const decoded = decodeLine(key, encoded);
      expect(decoded).toBe(msg);
    });

    it('should handle empty line', () => {
      expect(decodeLine('key', '')).toBe('');
    });
  });

  describe('encode', () => {
    it('should return empty string for empty message', () => {
      expect(encode('key', '')).toBe('');
    });

    it('should encode a single line', () => {
      const key = 'secret';
      const msg = 'hello';
      expect(encode(key, msg)).toBe(encodeLine(key, msg));
    });

    it('should encode multi-line messages with key reset per line', () => {
      const key = 'key';
      const msg = 'line1\nline2';
      const lines = msg.split('\n');
      const expected = lines.map(line => encodeLine(key, line)).join('\n');
      expect(encode(key, msg)).toBe(expected);
    });

    it('should reset key position at each newline', () => {
      const key = 'AB';
      const msg = 'AA\nAA';
      const encoded = encode(key, msg);
      // Each line starts with key[0]='A', so both lines should encode identically
      const parts = encoded.split('\n');
      expect(parts[0]).toBe(parts[1]);
    });
  });

  describe('decode', () => {
    it('should return empty string for empty ciphertext', () => {
      expect(decode('key', '')).toBe('');
    });

    it('should round-trip with encode', () => {
      const key = 'MySecretKey';
      const msg = 'Hello, World!\nThis is a test.';
      const encoded = encode(key, msg);
      const decoded = decode(key, encoded);
      expect(decoded).toBe(msg);
    });

    it('should decode multi-line ciphertext with key reset per line', () => {
      const key = 'test';
      const msg = 'first line\nsecond line\nthird line';
      const encoded = encode(key, msg);
      expect(decode(key, encoded)).toBe(msg);
    });
  });

  describe('cross-validation with Python reference', () => {
    it('should produce output consistent with the Python formula', () => {
      // Manually compute: key='A' (65), message='Hello'
      // H=72, e=101, l=108, l=108, o=111
      // shift for A = (65-32)%94+1 = 33%94+1 = 34
      // H: (72-32+34)%95+32 = 74%95+32 = 74+32 = 106 → 'j'
      // e: (101-32+34)%95+32 = 103%95+32 = 8+32 = 40 → '('
      // l: (108-32+34)%95+32 = 110%95+32 = 15+32 = 47 → '/'
      // l: (108-32+34)%95+32 = 110%95+32 = 15+32 = 47 → '/'
      // o: (111-32+34)%95+32 = 113%95+32 = 18+32 = 50 → '2'
      const result = encode('A', 'Hello');
      expect(result).toBe('j(//2');
    });
  });
});
