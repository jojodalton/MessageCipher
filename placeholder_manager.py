"""Placeholder text state management for input fields.

Provides pure logic for managing placeholder visibility in text fields,
decoupled from the UI rendering layer. Each field gets its own PlaceholderState
instance to track whether the placeholder is currently displayed.
"""


class PlaceholderState:
    """Tracks placeholder visibility state for a single field."""

    def __init__(self, placeholder_text: str):
        """Initialize with the placeholder text to display when field is empty.

        Args:
            placeholder_text: The hint text shown when the field has no user content.
        """
        self.placeholder_text = placeholder_text
        self.is_showing_placeholder = True

    def on_focus_in(self, current_content: str) -> tuple[bool, str]:
        """Handle focus-in event.

        When the field gains focus, determine whether the placeholder should be
        cleared so the user can start typing.

        Args:
            current_content: The current text content of the widget.

        Returns:
            (should_clear, cursor_position) - whether to clear field content
            and where to place the cursor. cursor_position is "0" for the
            beginning of an entry, or "1.0" for a text widget.
        """
        if self.is_showing_placeholder:
            self.is_showing_placeholder = False
            return (True, "1.0")
        return (False, "")

    def on_focus_out(self, current_content: str) -> tuple[bool, str]:
        """Handle focus-out event.

        When the field loses focus, determine whether the placeholder should be
        restored (i.e., when the field is empty).

        Args:
            current_content: The current text content of the widget.

        Returns:
            (should_show_placeholder, placeholder_text) - whether to display
            the placeholder text in the field.
        """
        if current_content.strip() == "":
            self.is_showing_placeholder = True
            return (True, self.placeholder_text)
        return (False, "")

    def get_real_content(self, widget_content: str) -> str:
        """Return actual user content, excluding placeholder text.

        When the placeholder is being displayed, the widget contains the
        placeholder string but that should not be treated as user input.

        Args:
            widget_content: The raw text content from the widget.

        Returns:
            Empty string if placeholder is showing, otherwise the widget content
            unchanged.
        """
        if self.is_showing_placeholder:
            return ""
        return widget_content
