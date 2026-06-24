"""Modern MessageCipher application shell using customtkinter.

Provides the main application window with all UI components arranged in a
responsive grid layout. Initializes theming, instantiates components, and
wires up keyboard shortcuts and callbacks.
"""

from __future__ import annotations

import sys
import tkinter
import tkinter.messagebox

try:
    import customtkinter as ctk
except (ImportError, ModuleNotFoundError):
    tkinter.messagebox.showerror(
        "Error",
        "customtkinter is unavailable. Please install it with: pip install customtkinter",
    )
    sys.exit(1)

from version import VERSION
from theme_engine import ThemeEngine
from header_bar import HeaderBar
from key_input_row import KeyInputRow
from card_panel import CardPanel
from action_bar import ActionBar
from status_banner_ui import StatusBanner
from keyboard_shortcuts import SHORTCUTS, is_reserved
from input_validation import is_valid_key, find_forbidden_positions, is_copy_eligible
import message_cipher


class MessageCipherApp(ctk.CTk):
    """Main application window for the modern MessageCipher UI.

    Arranges all components in a vertical grid layout:
        Row 0: HeaderBar (fixed height)
        Row 1: KeyInputRow (fixed height)
        Row 2: MessagePanel - CardPanel (weight=1, expands)
        Row 3: ActionBar (fixed height)
        Row 4: StatusBanner (fixed height)
        Row 5: CipherPanel - CardPanel (weight=1, expands)
    """

    _PADDING = 12  # Consistent spacing between panels and window edges

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title(f"MessageCipher v{VERSION}")
        self.minsize(700, 500)

        # Initialize theme engine and set appearance mode
        self.theme_engine = ThemeEngine()
        ctk.set_appearance_mode(self.theme_engine.get_current_mode())

        # Configure root grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # HeaderBar - fixed
        self.grid_rowconfigure(1, weight=0)  # KeyInputRow - fixed
        self.grid_rowconfigure(2, weight=1)  # MessagePanel - expands
        self.grid_rowconfigure(3, weight=0)  # ActionBar - fixed
        self.grid_rowconfigure(4, weight=0)  # StatusBanner - fixed
        self.grid_rowconfigure(5, weight=1)  # CipherPanel - expands

        # Create all components
        self._setup_layout()

        # Bind keyboard shortcuts
        self._bind_shortcuts()

    def _setup_layout(self) -> None:
        """Create all UI components and place them in the grid."""
        pad = self._PADDING

        # Row 0: HeaderBar
        self.header_bar = HeaderBar(
            self,
            version=VERSION,
            toggle_callback=self._on_theme_toggle,
            current_mode=self.theme_engine.get_current_mode(),
        )
        self.header_bar.grid(
            row=0, column=0, sticky="ew", padx=pad, pady=(pad, 0)
        )

        # Row 1: KeyInputRow
        self.key_input = KeyInputRow(self)
        self.key_input.grid(
            row=1, column=0, sticky="ew", padx=pad, pady=(pad, 0)
        )

        # Row 2: MessagePanel (CardPanel)
        self.message_panel = CardPanel(
            self, placeholder="Type or paste your message here..."
        )
        self.message_panel.grid(
            row=2, column=0, sticky="nsew", padx=pad, pady=(pad, 0)
        )
        self.message_panel.set_copy_callback(
            lambda text: self.copy_to_clipboard("message")
        )

        # Row 3: ActionBar
        self.action_bar = ActionBar(
            self,
            encode_callback=self.on_encode,
            decode_callback=self.on_decode,
            clear_callback=self.on_clear,
            accent_color=self.theme_engine.get_scheme()["accent"],
        )
        self.action_bar.grid(
            row=3, column=0, sticky="ew", padx=pad, pady=(pad, 0)
        )

        # Row 4: StatusBanner
        self.status_banner = StatusBanner(self)
        self.status_banner.grid(
            row=4, column=0, sticky="ew", padx=pad, pady=(pad, 0)
        )

        # Row 5: CipherPanel (CardPanel)
        self.cipher_panel = CardPanel(
            self, placeholder="Ciphertext appears here..."
        )
        self.cipher_panel.grid(
            row=5, column=0, sticky="nsew", padx=pad, pady=pad
        )
        self.cipher_panel.set_copy_callback(
            lambda text: self.copy_to_clipboard("cipher")
        )

    def _bind_shortcuts(self) -> None:
        """Register keyboard shortcuts, preventing default text behavior."""
        for sequence, action in SHORTCUTS.items():
            if is_reserved(sequence):
                continue
            if action == "encode":
                self.bind(sequence, self._shortcut_encode)
            elif action == "decode":
                self.bind(sequence, self._shortcut_decode)
            elif action == "clear":
                self.bind(sequence, self._shortcut_clear)

    def _shortcut_encode(self, event=None) -> str:
        """Handle Ctrl+E shortcut."""
        self.on_encode()
        return "break"

    def _shortcut_decode(self, event=None) -> str:
        """Handle Ctrl+D shortcut."""
        self.on_decode()
        return "break"

    def _shortcut_clear(self, event=None) -> str:
        """Handle Ctrl+L shortcut."""
        self.on_clear()
        return "break"

    def on_encode(self) -> None:
        """Execute encode operation with validation and feedback."""
        # Clear previous state
        self.status_banner.clear()
        self.message_panel.clear_highlights()
        self.cipher_panel.clear_highlights()

        # Validate key
        key = self.key_input.get_content()
        valid, error_msg = is_valid_key(key)
        if not valid:
            self.status_banner.show_error(error_msg)
            self.key_input.flash_border(
                self.theme_engine.get_scheme()["error"], 1000
            )
            return

        # Get message content
        message_text = self.message_panel.get_content()
        if not message_text:
            self.status_banner.show_error("Message must not be empty")
            return

        # Check forbidden characters in message (allow newlines — they are preserved as-is)
        forbidden = find_forbidden_positions(message_text, allow_newline=True)
        if forbidden:
            self.message_panel.highlight_forbidden()
            self.status_banner.show_error(
                "Message contains forbidden characters (only printable ASCII 32-126 allowed)"
            )
            self.message_panel.flash_border(
                self.theme_engine.get_scheme()["error"], 1000
            )
            return

        # Perform encoding — encode each line separately to preserve newlines
        # (compatible with v0.2 behavior: key cycling resets per line)
        try:
            lines = message_text.split("\n")
            ciphertext = "\n".join(message_cipher.encode(key, line) for line in lines)
            self.cipher_panel.set_content(ciphertext)
            self.status_banner.show_success("Encoded successfully")
            self.cipher_panel.flash_border(
                self.theme_engine.get_scheme()["accent"], 1000
            )
        except (ValueError, TypeError) as e:
            self.status_banner.show_error(str(e))

    def on_decode(self) -> None:
        """Execute decode operation with validation and feedback."""
        # Clear previous state
        self.status_banner.clear()
        self.message_panel.clear_highlights()
        self.cipher_panel.clear_highlights()

        # Validate key
        key = self.key_input.get_content()
        valid, error_msg = is_valid_key(key)
        if not valid:
            self.status_banner.show_error(error_msg)
            self.key_input.flash_border(
                self.theme_engine.get_scheme()["error"], 1000
            )
            return

        # Get ciphertext content
        cipher_text = self.cipher_panel.get_content()
        if not cipher_text:
            self.status_banner.show_error("Ciphertext must not be empty")
            return

        # Check forbidden characters in ciphertext (allow newlines — they separate lines)
        forbidden = find_forbidden_positions(cipher_text, allow_newline=True)
        if forbidden:
            self.cipher_panel.highlight_forbidden()
            self.status_banner.show_error(
                "Ciphertext contains forbidden characters (only printable ASCII 32-126 allowed)"
            )
            self.cipher_panel.flash_border(
                self.theme_engine.get_scheme()["error"], 1000
            )
            return

        # Perform decoding — decode each line separately to preserve newlines
        # (compatible with v0.2 behavior: key cycling resets per line)
        try:
            lines = cipher_text.split("\n")
            plaintext = "\n".join(message_cipher.decode(key, line) for line in lines)
            self.message_panel.set_content(plaintext)
            self.status_banner.show_success("Decoded successfully")
            self.message_panel.flash_border(
                self.theme_engine.get_scheme()["accent"], 1000
            )
        except (ValueError, TypeError) as e:
            self.status_banner.show_error(str(e))

    def on_clear(self) -> None:
        """Reset all fields, highlights, and status."""
        self.key_input.clear()
        self.message_panel.set_content("")
        self.cipher_panel.set_content("")
        self.message_panel.clear_highlights()
        self.cipher_panel.clear_highlights()
        self.status_banner.clear()

    def copy_to_clipboard(self, source: str) -> None:
        """Copy text from specified panel to clipboard with eligibility check.

        Args:
            source: Either "message" or "cipher" to indicate which panel to copy from.
        """
        if source == "message":
            content = self.message_panel.get_content()
        elif source == "cipher":
            content = self.cipher_panel.get_content()
        else:
            return

        if not is_copy_eligible(content):
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.status_banner.show_success("Copied to clipboard")
        except tkinter.TclError:
            self.status_banner.show_error("Failed to copy to clipboard")

    def _on_theme_toggle(self) -> None:
        """Handle theme toggle from HeaderBar."""
        new_mode = self.theme_engine.toggle()
        ctk.set_appearance_mode(new_mode)
        self.header_bar.update_mode(new_mode)


if __name__ == "__main__":
    app = MessageCipherApp()
    app.mainloop()
