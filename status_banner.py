"""Status banner controller for toast-style notifications.

Manages banner display state, auto-dismiss logic, and message formatting
for the MessageCipher modern UI. Separates notification logic from
the GUI layer for testability.
"""

from enum import Enum
from dataclasses import dataclass
import time


class BannerType(Enum):
    """Types of status banners."""
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class BannerState:
    """Represents the current state of a status banner.

    Attributes:
        message: Display text, truncated to 200 characters max.
        banner_type: SUCCESS or ERROR.
        auto_dismiss: True for success banners, False for error banners.
        dismiss_after_ms: 5000 for success (auto-dismiss delay), 0 for error (manual).
        timestamp: time.time() when the banner was created.
    """
    message: str
    banner_type: BannerType
    auto_dismiss: bool
    dismiss_after_ms: int
    timestamp: float


class StatusBannerState:
    """Manages status banner display state and auto-dismiss logic."""

    MAX_MESSAGE_LENGTH = 200
    SUCCESS_DISMISS_MS = 5000

    def show(self, message: str, banner_type: BannerType) -> dict:
        """Create a new banner state.

        A new banner replaces any previously visible banner.

        Args:
            message: The status message to display.
            banner_type: SUCCESS or ERROR.

        Returns:
            Dict with keys: message, type, auto_dismiss, dismiss_after_ms
        """
        formatted = self.format_message(message)
        auto_dismiss = self.should_auto_dismiss(banner_type)
        dismiss_after_ms = self.SUCCESS_DISMISS_MS if auto_dismiss else 0

        self._current = BannerState(
            message=formatted,
            banner_type=banner_type,
            auto_dismiss=auto_dismiss,
            dismiss_after_ms=dismiss_after_ms,
            timestamp=time.time(),
        )

        return {
            "message": formatted,
            "type": banner_type.value,
            "auto_dismiss": auto_dismiss,
            "dismiss_after_ms": dismiss_after_ms,
        }

    def should_auto_dismiss(self, banner_type: BannerType) -> bool:
        """Determine if a banner should auto-dismiss based on its type.

        Success messages auto-dismiss after 5 seconds.
        Error messages persist until user action.

        Args:
            banner_type: The type of banner.

        Returns:
            True for SUCCESS, False for ERROR.
        """
        return banner_type == BannerType.SUCCESS

    def format_message(self, message: str) -> str:
        """Format a message for banner display by truncating to 200 chars max.

        Args:
            message: The raw message string.

        Returns:
            The message truncated to at most 200 characters.
        """
        if len(message) <= self.MAX_MESSAGE_LENGTH:
            return message
        return message[:self.MAX_MESSAGE_LENGTH]
