"""Reusable card-styled panel component for MessageCipher modern UI.

Provides a CTkFrame-based container with a CTkTextbox, copy button,
character counter label, placeholder text management, and visual feedback
methods (highlight forbidden characters, flash border).
"""

import customtkinter as ctk

from input_validation import count_characters, find_forbidden_positions, is_copy_eligible
from placeholder_manager import PlaceholderState


class CardPanel(ctk.CTkFrame):
    """A card-styled container with border/shadow, text area, copy button, and counter."""

    _FORBIDDEN_TAG = "forbidden"
    _PLACEHOLDER_COLOR = "gray"

    def __init__(self, parent, placeholder: str, **kwargs):
        """Initialize the card panel.

        Args:
            parent: Parent widget.
            placeholder: Placeholder text displayed when empty and unfocused.
            **kwargs: Additional keyword arguments passed to CTkFrame.
        """
        # Ensure a visible border of at least 1px
        kwargs.setdefault("border_width", 2)
        kwargs.setdefault("corner_radius", 8)

        super().__init__(parent, **kwargs)

        self._placeholder_state = PlaceholderState(placeholder)
        self._default_border_color = kwargs.get("border_color", self.cget("border_color"))
        self._flash_after_id: str | None = None

        # Configure grid layout: textbox expands, bottom row for counter/button
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Text area ---
        self._textbox = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=13),
            corner_radius=6,
        )
        self._textbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=(8, 4))

        # Configure the forbidden character highlight tag
        self._textbox._textbox.tag_configure(
            self._FORBIDDEN_TAG, background="#ff4444", foreground="white"
        )

        # --- Bottom row: character counter on left, copy button on right ---
        self._counter_label = ctk.CTkLabel(
            self,
            text="0 characters",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self._counter_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))

        self._copy_button = ctk.CTkButton(
            self,
            text="📋 Copy",
            width=80,
            height=28,
            font=ctk.CTkFont(size=11),
            command=self._on_copy,
        )
        self._copy_button.grid(row=1, column=1, sticky="e", padx=8, pady=(0, 8))

        # --- Placeholder setup ---
        self._show_placeholder()

        # --- Bind events ---
        self._textbox._textbox.bind("<FocusIn>", self._on_focus_in)
        self._textbox._textbox.bind("<FocusOut>", self._on_focus_out)
        self._textbox._textbox.bind("<KeyRelease>", self._on_content_changed)
        self._textbox._textbox.bind("<<Paste>>", self._on_paste)

        # Store the copy callback (can be overridden externally)
        self._copy_callback = None

    def set_copy_callback(self, callback) -> None:
        """Set an external callback for copy operations.

        The callback receives the text content as its argument.
        If not set, the panel copies directly to the clipboard.
        """
        self._copy_callback = callback

    # --- Public API ---

    def get_content(self) -> str:
        """Return text content excluding placeholder.

        Returns the actual user-entered text. If the placeholder is showing,
        returns an empty string.
        """
        raw = self._textbox.get("1.0", "end-1c")
        return self._placeholder_state.get_real_content(raw)

    def set_content(self, text: str) -> None:
        """Set text content and update character counter.

        Clears any placeholder, inserts the provided text, and refreshes
        the character counter display.
        """
        self._placeholder_state.is_showing_placeholder = False
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        if text:
            self._textbox.insert("1.0", text)
            self._apply_normal_style()
        else:
            # If setting empty content, restore placeholder
            self._show_placeholder()
        self._update_counter()

    def get_character_count(self) -> int:
        """Return current character count (excludes trailing newline)."""
        content = self.get_content()
        return count_characters(content)

    def highlight_forbidden(self) -> bool:
        """Highlight forbidden chars with red background.

        Scans the text content for characters outside printable ASCII (32-126),
        excluding newlines, and highlights each one individually.

        Returns:
            True if any forbidden characters were found, False otherwise.
        """
        self.clear_highlights()
        content = self.get_content()
        if not content:
            return False

        positions = find_forbidden_positions(content, allow_newline=True)
        if not positions:
            return False

        inner_textbox = self._textbox._textbox
        for pos in positions:
            # Convert linear position to tkinter text index (line.col)
            line = content[:pos].count("\n") + 1
            col = pos - content[:pos].rfind("\n") - 1
            start = f"{line}.{col}"
            end = f"{line}.{col + 1}"
            inner_textbox.tag_add(self._FORBIDDEN_TAG, start, end)

        return True

    def clear_highlights(self) -> None:
        """Remove all error highlights from the text area."""
        inner_textbox = self._textbox._textbox
        inner_textbox.tag_remove(self._FORBIDDEN_TAG, "1.0", "end")

    def flash_border(self, color: str, duration_ms: int = 1000) -> None:
        """Temporarily change border color for visual feedback.

        Changes the border to the specified color, then reverts after
        duration_ms milliseconds.

        Args:
            color: The temporary border color (e.g., accent for success, error for errors).
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
            # Fallback: use a neutral border
            self.configure(border_color="gray")

    def _show_placeholder(self) -> None:
        """Display placeholder text in the textbox with dimmed styling."""
        self._placeholder_state.is_showing_placeholder = True
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("1.0", self._placeholder_state.placeholder_text)
        self._textbox._textbox.configure(fg="gray")

    def _apply_normal_style(self) -> None:
        """Apply normal text color (not placeholder)."""
        # Let customtkinter manage the actual text color based on theme
        self._textbox._textbox.configure(fg=self._textbox._textbox.cget("insertbackground"))

    def _on_focus_in(self, event=None) -> None:
        """Handle focus-in: clear placeholder if showing."""
        current = self._textbox.get("1.0", "end-1c")
        should_clear, _ = self._placeholder_state.on_focus_in(current)
        if should_clear:
            self._textbox.delete("1.0", "end")
            self._apply_normal_style()

    def _on_focus_out(self, event=None) -> None:
        """Handle focus-out: restore placeholder if content is empty."""
        current = self._textbox.get("1.0", "end-1c")
        should_show, placeholder_text = self._placeholder_state.on_focus_out(current)
        if should_show:
            self._show_placeholder()
        self._update_counter()

    def _on_content_changed(self, event=None) -> None:
        """Handle key release: update character counter live."""
        if not self._placeholder_state.is_showing_placeholder:
            self._update_counter()

    def _on_paste(self, event=None) -> None:
        """Handle paste event: update counter after paste completes."""
        # Schedule counter update after the paste is processed
        self.after(10, self._update_counter)

    def _update_counter(self) -> None:
        """Update the character counter label with current count."""
        count = self.get_character_count()
        self._counter_label.configure(text=f"{count} characters")

    def _on_copy(self) -> None:
        """Handle copy button click."""
        content = self.get_content()
        if not is_copy_eligible(content):
            return

        if self._copy_callback:
            self._copy_callback(content)
        else:
            # Default: copy directly to clipboard
            try:
                self.clipboard_clear()
                self.clipboard_append(content)
            except Exception:
                pass
