# Release Notes

## v0.3 — 2026-06-23

**Modern UI Redesign**

Complete visual overhaul of the application using customtkinter.

### What's new

- Dark/light mode with system detection and persistent preference
- Card-based layout with distinct message and cipher panels
- Header bar showing app title, version, and theme toggle
- Styled key input with visibility toggle (masked by default)
- Keyboard shortcuts: Ctrl+E (encode), Ctrl+D (decode), Ctrl+L (clear)
- Copy-to-clipboard buttons on both panels
- Live character counters on message and cipher areas
- Toast-style status banner (green for success, red for errors, auto-dismiss)
- Forbidden character highlighting (red background on invalid chars)
- Visual feedback: button hover effects, border flashing on success/error
- Responsive layout with minimum window size (700×500)
- Placeholder text in empty fields
- Graceful fallback if customtkinter is not installed

### Changed

- UI entry point moved from `cipher_ui.py` to `cipher_ui_modern.py`
- PyInstaller spec updated to package the new UI and all modules

---

## v0.2 — 2026-06-22

**App Versioning**

- Added `version.py` module with VERSION and BUILD_TIMESTAMP constants
- Added `bump_version.py` pre-build script for automatic version increment
- Version displayed in window title and CLI startup
- Version parsing, formatting, comparison, and validation utilities

---

## v0.1

**Initial Release**

- Core cipher encode/decode logic (`message_cipher.py`)
- Basic tkinter GUI (`cipher_ui.py`)
- CLI interface (`cipher_cli.py`)
