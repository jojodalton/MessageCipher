/**
 * Unit tests for ui.js — DOM Manipulation Module
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

// Set up a minimal DOM before importing the module
function setupDOM() {
  const dom = new JSDOM(`
    <html>
      <body>
        <input id="key-input" type="text" value="" />
        <textarea id="message-textarea"></textarea>
        <textarea id="ciphertext-textarea"></textarea>
        <div id="status-banner" class="status-banner" aria-live="polite" hidden></div>
      </body>
    </html>
  `);

  global.document = dom.window.document;
  return dom;
}

describe('ui.js', () => {
  let ui;

  beforeEach(async () => {
    setupDOM();
    // Dynamic import to pick up the fresh global document
    ui = await import('../src/ui.js');
  });

  describe('showStatus', () => {
    it('should display a success message with appropriate class', () => {
      ui.showStatus('Encoded successfully', 'success');
      const banner = document.getElementById('status-banner');

      expect(banner.textContent).toBe('Encoded successfully');
      expect(banner.className).toBe('status-banner status-success');
      expect(banner.hidden).toBe(false);
    });

    it('should display an error message with appropriate class', () => {
      ui.showStatus('Key must not be empty', 'error');
      const banner = document.getElementById('status-banner');

      expect(banner.textContent).toBe('Key must not be empty');
      expect(banner.className).toBe('status-banner status-error');
      expect(banner.hidden).toBe(false);
    });
  });

  describe('clearStatus', () => {
    it('should clear the status banner content and hide it', () => {
      // First show a message
      ui.showStatus('Some message', 'success');
      // Then clear it
      ui.clearStatus();

      const banner = document.getElementById('status-banner');
      expect(banner.textContent).toBe('');
      expect(banner.className).toBe('status-banner');
      expect(banner.hidden).toBe(true);
    });
  });

  describe('clearAllFields', () => {
    it('should empty all input fields and clear status', () => {
      // Set some values
      document.getElementById('key-input').value = 'secret';
      document.getElementById('message-textarea').value = 'Hello';
      document.getElementById('ciphertext-textarea').value = 'Cipher';
      ui.showStatus('Success', 'success');

      ui.clearAllFields();

      expect(document.getElementById('key-input').value).toBe('');
      expect(document.getElementById('message-textarea').value).toBe('');
      expect(document.getElementById('ciphertext-textarea').value).toBe('');
      expect(document.getElementById('status-banner').textContent).toBe('');
      expect(document.getElementById('status-banner').hidden).toBe(true);
    });
  });

  describe('getKeyValue', () => {
    it('should return the key input value', () => {
      document.getElementById('key-input').value = 'mykey';
      expect(ui.getKeyValue()).toBe('mykey');
    });

    it('should return empty string when field is empty', () => {
      expect(ui.getKeyValue()).toBe('');
    });
  });

  describe('getMessageValue', () => {
    it('should return the message textarea value', () => {
      document.getElementById('message-textarea').value = 'Hello world';
      expect(ui.getMessageValue()).toBe('Hello world');
    });
  });

  describe('getCiphertextValue', () => {
    it('should return the ciphertext textarea value', () => {
      document.getElementById('ciphertext-textarea').value = 'encoded text';
      expect(ui.getCiphertextValue()).toBe('encoded text');
    });
  });

  describe('setMessageValue', () => {
    it('should set the message textarea value', () => {
      ui.setMessageValue('New message');
      expect(document.getElementById('message-textarea').value).toBe('New message');
    });
  });

  describe('setCiphertextValue', () => {
    it('should set the ciphertext textarea value', () => {
      ui.setCiphertextValue('New ciphertext');
      expect(document.getElementById('ciphertext-textarea').value).toBe('New ciphertext');
    });
  });

  describe('updateCopyButtonState', () => {
    it('should disable button when textarea is empty', () => {
      const textarea = document.getElementById('message-textarea');
      const button = document.createElement('button');
      button.disabled = false;
      textarea.value = '';

      ui.updateCopyButtonState(textarea, button);
      expect(button.disabled).toBe(true);
    });

    it('should disable button when textarea contains only whitespace', () => {
      const textarea = document.getElementById('message-textarea');
      const button = document.createElement('button');
      button.disabled = false;
      textarea.value = '   \n\t  ';

      ui.updateCopyButtonState(textarea, button);
      expect(button.disabled).toBe(true);
    });

    it('should enable button when textarea has non-whitespace content', () => {
      const textarea = document.getElementById('message-textarea');
      const button = document.createElement('button');
      button.disabled = true;
      textarea.value = 'Hello';

      ui.updateCopyButtonState(textarea, button);
      expect(button.disabled).toBe(false);
    });

    it('should handle null textarea gracefully', () => {
      const button = document.createElement('button');
      // Should not throw
      ui.updateCopyButtonState(null, button);
    });

    it('should handle null button gracefully', () => {
      const textarea = document.getElementById('message-textarea');
      // Should not throw
      ui.updateCopyButtonState(textarea, null);
    });
  });
});
