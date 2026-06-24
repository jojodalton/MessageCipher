"""ActionBar component for the MessageCipher modern UI.

Provides a horizontally centered bar with Encode, Decode, and Clear buttons.
Each button displays a directional symbol and keyboard shortcut hint.
Encode and Decode use the accent color as primary action buttons.
"""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from keyboard_shortcuts import get_shortcut_label


class ActionBar(ctk.CTkFrame):
    """Centered action bar with Encode, Decode, and Clear buttons.

    The bar has a fixed height and centers its buttons horizontally.
    Encode and Decode buttons use the accent color to indicate primary actions.

    Args:
        parent: Parent widget.
        encode_callback: Callable invoked when the Encode button is clicked.
        decode_callback: Callable invoked when the Decode button is clicked.
        clear_callback: Callable invoked when the Clear button is clicked.
        accent_color: Color for primary action buttons (Encode/Decode).
        height: Fixed height of the action bar in pixels.
        **kwargs: Additional keyword arguments passed to CTkFrame.
    """

    ACTION_BAR_HEIGHT: int = 56

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        encode_callback: Callable[[], None] | None = None,
        decode_callback: Callable[[], None] | None = None,
        clear_callback: Callable[[], None] | None = None,
        accent_color: str | None = None,
        height: int | None = None,
        **kwargs,
    ):
        bar_height = height if height is not None else self.ACTION_BAR_HEIGHT
        super().__init__(parent, height=bar_height, **kwargs)

        self._encode_callback = encode_callback
        self._decode_callback = decode_callback
        self._clear_callback = clear_callback
        self._accent_color = accent_color or "#0096c7"

        # Prevent the frame from shrinking to fit children
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Configure grid: 3 columns with equal weight for centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout the Encode, Decode, and Clear buttons."""
        # Get shortcut labels from keyboard_shortcuts module
        encode_hint = get_shortcut_label("encode")
        decode_hint = get_shortcut_label("decode")
        clear_hint = get_shortcut_label("clear")

        # Encode button: downward arrow symbol with shortcut hint
        encode_text = f"\u25bc Encode  {encode_hint}"
        self._encode_button = ctk.CTkButton(
            self,
            text=encode_text,
            command=self._on_encode,
            fg_color=self._accent_color,
            hover_color=self._darken_color(self._accent_color),
            width=150,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._encode_button.grid(row=0, column=1, padx=(0, 8), pady=8)

        # Decode button: upward arrow symbol with shortcut hint
        decode_text = f"\u25b2 Decode  {decode_hint}"
        self._decode_button = ctk.CTkButton(
            self,
            text=decode_text,
            command=self._on_decode,
            fg_color=self._accent_color,
            hover_color=self._darken_color(self._accent_color),
            width=150,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._decode_button.grid(row=0, column=2, padx=8, pady=8)

        # Clear button: shortcut hint only, no accent color (secondary action)
        clear_text = f"Clear  {clear_hint}"
        self._clear_button = ctk.CTkButton(
            self,
            text=clear_text,
            command=self._on_clear,
            width=120,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
        )
        self._clear_button.grid(row=0, column=3, padx=(8, 0), pady=8)

    def _on_encode(self) -> None:
        """Handle Encode button click."""
        if self._encode_callback is not None:
            self._encode_callback()

    def _on_decode(self) -> None:
        """Handle Decode button click."""
        if self._decode_callback is not None:
            self._decode_callback()

    def _on_clear(self) -> None:
        """Handle Clear button click."""
        if self._clear_callback is not None:
            self._clear_callback()

    @staticmethod
    def _darken_color(hex_color: str) -> str:
        """Darken a hex color by 15% for hover effect.

        Args:
            hex_color: A hex color string (e.g., "#0096c7").

        Returns:
            A darkened hex color string.
        """
        try:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            factor = 0.85
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return "#005f8a"
