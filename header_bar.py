"""HeaderBar component for the MessageCipher modern UI.

Displays the application title with version on the left and a theme toggle
control with theme indicator on the right. Fixed height, stretches horizontally.
"""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from version import VERSION


class HeaderBar(ctk.CTkFrame):
    """Toolbar-style header bar with title, version, and theme toggle.

    Args:
        parent: Parent widget.
        version: Version string to display (e.g., "0.2"). Defaults to VERSION from version.py.
        toggle_callback: Callable invoked when the theme toggle is activated.
            Should accept no arguments and handle theme switching.
        current_mode: Initial theme mode, either "dark" or "light".
        height: Fixed height of the header bar in pixels.
        **kwargs: Additional keyword arguments passed to CTkFrame.
    """

    HEADER_HEIGHT: int = 48

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        version: str | None = None,
        toggle_callback: Callable[[], None] | None = None,
        current_mode: str = "light",
        height: int | None = None,
        **kwargs,
    ):
        bar_height = height if height is not None else self.HEADER_HEIGHT
        super().__init__(parent, height=bar_height, **kwargs)

        self._version = version if version is not None else VERSION
        self._toggle_callback = toggle_callback
        self._current_mode = current_mode

        # Prevent the frame from shrinking to fit children
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Configure grid: column 0 expands (title), columns 1-2 fixed (indicator + toggle)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout all child widgets."""
        # Title label: "MessageCipher vX.Y.Z" left-aligned
        title_text = f"MessageCipher v{self._version}"
        self._title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        self._title_label.grid(row=0, column=0, sticky="w", padx=(12, 8), pady=8)

        # Theme indicator label (shows icon for current mode)
        self._theme_indicator = ctk.CTkLabel(
            self,
            text=self._get_theme_icon(),
            font=ctk.CTkFont(size=16),
            width=30,
        )
        self._theme_indicator.grid(row=0, column=1, sticky="e", padx=(4, 4), pady=8)

        # Theme toggle switch
        self._theme_switch = ctk.CTkSwitch(
            self,
            text="Dark Mode",
            command=self._on_toggle,
            width=100,
            onvalue=1,
            offvalue=0,
        )
        # Set initial switch state based on current mode
        if self._current_mode == "dark":
            self._theme_switch.select()
        else:
            self._theme_switch.deselect()

        self._theme_switch.grid(row=0, column=2, sticky="e", padx=(4, 12), pady=8)

    def _get_theme_icon(self) -> str:
        """Return an icon/label representing the current theme mode."""
        if self._current_mode == "dark":
            return "\U0001f319"  # 🌙 crescent moon
        return "\u2600\ufe0f"  # ☀️ sun

    def _on_toggle(self) -> None:
        """Handle theme toggle activation."""
        # Update internal mode
        self._current_mode = "dark" if self._current_mode == "light" else "light"
        # Update the theme indicator
        self._theme_indicator.configure(text=self._get_theme_icon())
        # Invoke the external callback if provided
        if self._toggle_callback is not None:
            self._toggle_callback()

    def update_mode(self, mode: str) -> None:
        """Update the displayed theme mode indicator and switch state.

        Args:
            mode: The new theme mode, either "dark" or "light".
        """
        self._current_mode = mode
        self._theme_indicator.configure(text=self._get_theme_icon())
        if mode == "dark":
            self._theme_switch.select()
        else:
            self._theme_switch.deselect()

    def get_current_mode(self) -> str:
        """Return the currently displayed theme mode."""
        return self._current_mode
