# MessageCipher

A modified Vigenère cipher tool for encoding and decoding messages using printable ASCII characters. Available as both a Python desktop application and a Progressive Web App.

## How It Works

MessageCipher uses a modified Vigenère cipher operating over the printable ASCII range (characters 32–126, 95 total). The key cycles through the message, with each key character producing a shift of 1–94 positions — no character ever maps to itself.

**Key behavior:**
- Key must be non-empty, max 1000 characters, all printable ASCII
- Messages allow printable ASCII plus newlines
- Key position resets at each newline (lines are encoded independently)
- Encoding and decoding are inverse operations: `decode(key, encode(key, msg)) == msg`

## Applications

### PWA (Progressive Web App)

A mobile-optimized browser-based cipher tool with offline support.

- **Live:** https://jojodalton.github.io/MessageCipher/
- **Location:** `pwa/`
- **Version:** 1.1.0
- **Tech:** Vanilla JavaScript ES modules, Service Worker, no build step

**Features:**
- Encode/decode with real-time forbidden character highlighting
- Hidden key field with visibility toggle
- Dark/light theme
- Copy/paste clipboard integration
- Version badge with release notes
- Force refresh button for cache busting
- Fully offline-capable

**Run locally:**
```bash
cd pwa
python -m http.server 8080
# Open http://localhost:8080
```

**Run tests:**
```bash
cd pwa
npm install
npm test
```

### Python Desktop App

A desktop GUI application using customtkinter. Can be packaged as a standalone Windows executable.

- **Location:** project root
- **Version:** 0.3
- **Tech:** Python 3, customtkinter, PyInstaller (for exe)

**Features:**
- Encode/decode with forbidden character highlighting
- Hidden key field with visibility toggle
- Dark/light theme
- Copy to clipboard
- Keyboard shortcuts (Ctrl+E encode, Ctrl+D decode, Ctrl+L clear)

**Run:**
```bash
pip install customtkinter
python cipher_ui_modern.py
```

**Build standalone exe (Windows):**
```bash
pip install pyinstaller
pyinstaller MessageCipher.spec
# Output: dist/MessageCipher_v0.3.exe
```

**Run tests:**
```bash
pip install hypothesis pytest
pytest
```

## Project Structure

```
MessageCipher/
├── pwa/                    # Progressive Web App
│   ├── src/                # JS modules (app, cipher, validator, etc.)
│   ├── tests/              # Vitest test files
│   ├── icons/              # PWA icons (192x192, 512x512)
│   ├── index.html          # App entry point
│   ├── style.css           # Styles (light/dark themes)
│   ├── service-worker.js   # Offline caching
│   ├── manifest.json       # PWA manifest
│   ├── version.json        # Version source of truth
│   └── release-notes.json  # Changelog
├── message_cipher.py       # Python cipher engine
├── input_validation.py     # Python validation functions
├── cipher_ui_modern.py     # Python desktop UI
├── version.py              # Python version
└── .github/workflows/      # CI/CD (tests + GitHub Pages deploy)
```

## Cipher Algorithm

Both implementations use the same shift formula:

```
shift = (keyCharCode - 32) % 94 + 1        // always 1..94
encode: (charCode - 32 + shift) % 95 + 32
decode: (charCode - 32 - shift + 95) % 95 + 32
```

This guarantees:
- Every character shifts by at least 1 position (no identity mapping)
- Output is always printable ASCII
- `decode(key, encode(key, text)) == text` for all valid inputs
