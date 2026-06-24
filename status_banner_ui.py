"""StatusBanner UI component for toast-style inline notifications.

Displays success (green background) or error (red background) messages
as a horizontal banner positioned between the action buttons and content area.
Uses StatusBannerState for logic (auto-dismiss timing, message formatting).
"""

from __future__ import annotations

import customtkinter as ctk

from status_banner import BannerType, StatusBannerState


class StatusBanner(ctk.CTkFrame):
    """Inline notification banner for success/error messages.

    Success messages auto-dismiss after 5 seconds via tkinter after().
    Error messages persist until the user performs any action.
    A new operation replaces any previous message, cancelling pending dismissals.
    Messages are truncated to 200 characters and displayed on a single line.

    Args:
        parent: Parent widget.
        **kwargs: Additional keyword arguments passed to CTkFrame.
    """

    # Colors for banner types
    _SUCCESS_BG = "#198754"
    _SUCCESS_FG = "#ffffff"
    _ERROR_BG = "#dc3545"
    _ERROR_FG = "#ffffff"

    _BANNER_HEIGHT = 32

    def __init__(self, parent: ctk.CTkBaseClass, **kwargs):
        kwargs.setdefault("height", self._BANNER_HEIGHT)
        kwargs.setdefault("corner_radius", 6)
        super().__init__(parent, **kwargs)

        self._state = StatusBannerState()
        self._dismiss_after_id: str | None = None

        # Prevent frame from resizing to fit children
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Configure grid: single row, label fills width
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Message label
        self._label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._label.grid(row=0, column=0, sticky="ew", padx=12, pady=4)

        # Start hidden
        self._visible = False
        self._hide()

    # --- Public API ---

    def show_success(self, message: str) -> None:
        """Display a success message with green background.

        The message auto-dismisses after 5 seconds. Any pending
        auto-dismiss from a previous message is cancelled first.

        Args:
            message: The success message to display.
        """
        self._cancel_pending_dismiss()

        result = self._state.show(message, BannerType.SUCCESS)

        self._apply_style(self._SUCCESS_BG, self._SUCCESS_FG)
        self._label.configure(text=f"✓ {result['message']}")
        self._show()

        # Schedule auto-dismiss
        self._dismiss_after_id = self.after(
            result["dismiss_after_ms"], self.clear
        )

    def show_error(self, message: str) -> None:
        """Display an error message with red background.

        The error persists until the user performs any action (cleared
        manually via clear()). Any pending auto-dismiss from a previous
        message is cancelled first.

        Args:
            message: The error message to display.
        """
        self._cancel_pending_dismiss()

        result = self._state.show(message, BannerType.ERROR)

        self._apply_style(self._ERROR_BG, self._ERROR_FG)
        self._label.configure(text=f"✗ {result['message']}")
        self._show()

    def clear(self) -> None:
        """Dismiss the banner manually, removing it from view.

        Cancels any pending auto-dismiss timer. Hides the banner and
        clears the message text.
        """
        self._cancel_pending_dismiss()
        self._label.configure(text="")
        self._hide()

    def is_visible(self) -> bool:
        """Return whether the banner is currently visible."""
        return self._visible

    # --- Private methods ---

    def _apply_style(self, bg_color: str, fg_color: str) -> None:
        """Apply background and foreground colors to the banner.

        Args:
            bg_color: Background color hex string.
            fg_color: Foreground (text) color hex string.
        """
        self.configure(fg_color=bg_color)
        self._label.configure(text_color=fg_color)

    def _show(self) -> None:
        """Make the banner visible."""
        self._visible = True
        # Restore the configured height so the banner is visible in the layout
        self.configure(height=self._BANNER_HEIGHT)

    def _hide(self) -> None:
        """Hide the banner from view by collapsing its height."""
        self._visible = False
        self.configure(height=0)

    def _cancel_pending_dismiss(self) -> None:
        """Cancel any pending auto-dismiss timer."""
        if self._dismiss_after_id is not None:
            self.after_cancel(self._dismiss_after_id)
            self._dismiss_after_id = None
