"""KeyInputRow component for the MessageCipher modern UI.

Provides a CTkFrame-based key input field with masked/revealed toggle,
placeholder text management, printable ASCII validation, and flash_border
support for error highlighting.
"""

from __future__ import annotations

import customtkinter as ctk

from input_validation import is_printable_ascii
from placeholder_manager import PlaceholderState


class KeyInputRow(ctk.CTkFrame):
    """Styled key input field with visibility toggle and validation.

    Features:
        - CTkEntry masked (show="*") by default
        - Visibility toggle button to reveal/mask key
        - PlaceholderState integration for "Enter cipher key..." placeholder
        - Printable ASCII validation (codes 32-126 only)
        - flash_border support for error highlighting

    Args:
        parent: Parent widget.
        placeholder: Placeholder text displayed when field is empty and unfocused.
        max_length: Maximum key length allowed. Defaults to 1000.
        **kwargs: Additional keyword arguments passed to CTkFrame.
    """

    _PLACEHOLDER_COLOR = "gray"
    _MAX_KEY_LENGTH = 1000
    _ROW_HEIGHT: int = 52

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        placeholder: str = "Enter cipher key...",
        max_length: int = 1000,
        **kwargs,
    ):
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("border_width", 2)
        kwargs.setdefault("height", self._ROW_HEIGHT)
        super().__init__(parent, **kwargs)

        self._placeholder_state = PlaceholderState(placeholder)
        self._max_length = max_length
        self._is_masked = True
        self._default_border_color = kwargs.get("border_color", self.cget("border_color"))
        self._flash_after_id: str | None = None

        # Prevent the frame from expanding vertically to fill extra space
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Configure grid: entry expands, toggle button fixed on right
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=0)

        # --- Key entry (masked by default) ---
        self._entry = ctk.CTkEntry(
            self,
            show="*",
            font=ctk.CTkFont(family="Consolas", size=13),
            corner_radius=6,
        )
        self._entry.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=8)

        # --- Visibility toggle button ---
        self._toggle_button = ctk.CTkButton(
            self,
            text="👁",
            width=36,
            height=32,
            font=ctk.CTkFont(size=14),
            command=self._on_toggle_visibility,
        )
        self._toggle_button.grid(row=0, column=1, sticky="e", padx=(0, 8), pady=8)

        # --- Placeholder setup ---
        self._show_placeholder()

        # --- Bind events ---
        self._entry.bind("<FocusIn>", self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._entry.bind("<KeyPress>", self._on_key_press)

    # --- Public API ---

    def get_content(self) -> str:
        """Return key content excluding placeholder text.

        Returns:
            The actual user-entered key text, or empty string if placeholder is showing.
        """
        raw = self._entry.get()
        return self._placeholder_state.get_real_content(raw)

    def set_content(self, text: str) -> None:
        """Set the key field content programmatically.

        Args:
            text: The key text to set. If empty, restores placeholder.
        """
        self._placeholder_state.is_showing_placeholder = False
        self._entry.configure(state="normal", show="*" if self._is_masked else "")
        self._entry.delete(0, "end")
        if text:
            self._entry.insert(0, text)
            self._apply_normal_style()
        else:
            self._show_placeholder()

    def clear(self) -> None:
        """Clear the key field and restore placeholder."""
        self._is_masked = True
        self._toggle_button.configure(text="👁")
        self.set_content("")

    def is_masked(self) -> bool:
        """Return whether the key is currently masked."""
        return self._is_masked

    def flash_border(self, color: str, duration_ms: int = 1000) -> None:
        """Temporarily change border color for error highlighting.

        Changes the border to the specified color, then reverts after
        duration_ms milliseconds.

        Args:
            color: The temporary border color (e.g., error red).
            duration_ms: How long the flash lasts in milliseconds (default 1000).
        """
        # Cancel any pending flash revert
        if self._flash_after_id is not None:
            self.after_cancel(self._flash_after_id)
            self._flash_after_id = None

        self.configure(border_color=color)
        self._flash_after_id = self.after(duration_ms, self._revert_border)

    # --- Private methods ---

    def _revert_border(self) -> None:
        """Revert border color to default."""
        self._flash_after_id = None
        if self._default_border_color:
            self.configure(border_color=self._default_border_color)
        else:
            self.configure(border_color="gray")

    def _on_toggle_visibility(self) -> None:
        """Toggle between masked and revealed key display."""
        if self._placeholder_state.is_showing_placeholder:
            # Don't toggle visibility when placeholder is showing
            return

        if self._is_masked:
            # Reveal key characters
            self._is_masked = False
            self._entry.configure(show="")
            self._toggle_button.configure(text="🙈")
        else:
            # Mask key characters
            self._is_masked = True
            self._entry.configure(show="*")
            self._toggle_button.configure(text="👁")

    def _show_placeholder(self) -> None:
        """Display placeholder text in the entry with dimmed styling."""
        self._placeholder_state.is_showing_placeholder = True
        self._entry.configure(state="normal", show="")
        self._entry.delete(0, "end")
        self._entry.insert(0, self._placeholder_state.placeholder_text)
        self._entry.configure(text_color=self._PLACEHOLDER_COLOR)

    def _apply_normal_style(self) -> None:
        """Apply normal text styling (not placeholder)."""
        # Reset to default text color by using the themed default
        self._entry.configure(
            text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"]
        )

    def _on_focus_in(self, event=None) -> None:
        """Handle focus-in: clear placeholder if showing."""
        current = self._entry.get()
        should_clear, _ = self._placeholder_state.on_focus_in(current)
        if should_clear:
            self._entry.configure(show="*" if self._is_masked else "")
            self._entry.delete(0, "end")
            self._apply_normal_style()

    def _on_focus_out(self, event=None) -> None:
        """Handle focus-out: restore placeholder if content is empty."""
        current = self._entry.get()
        should_show, _ = self._placeholder_state.on_focus_out(current)
        if should_show:
            self._show_placeholder()

    def _on_key_press(self, event) -> str | None:
        """Validate key input: accept only printable ASCII (32-126).

        Blocks any character outside the printable ASCII range.
        Also enforces the maximum key length.

        Returns:
            "break" to prevent the character from being inserted if invalid,
            None to allow normal processing.
        """
        # Allow control keys (backspace, delete, arrow keys, etc.)
        if not event.char or len(event.char) != 1:
            return None

        # Allow if placeholder was just cleared (event may fire during clear)
        if self._placeholder_state.is_showing_placeholder:
            return None

        char = event.char

        # Control characters (e.g., Ctrl+A, Ctrl+C) have char codes < 32
        # but are not printable input — let them pass for shortcuts
        if ord(char) < 32:
            return None

        # Reject non-printable ASCII
        if not is_printable_ascii(char):
            self.flash_border("#e63946", 1000)
            return "break"

        # Enforce max length
        current_content = self._entry.get()
        if len(current_content) >= self._max_length:
            return "break"

        return None
