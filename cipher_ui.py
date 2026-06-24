"""Simple GUI for the message cipher module using tkinter."""

import tkinter as tk
from tkinter import messagebox

from message_cipher import encode, decode, PRINTABLE_START, PRINTABLE_END
from version import VERSION, BUILD_TIMESTAMP


def is_printable_ascii(ch):
    """Check if a character is in printable ASCII range (32-126) or is a newline."""
    return PRINTABLE_START <= ord(ch) <= PRINTABLE_END or ch == "\n"


def highlight_forbidden(text_widget, tag_name="forbidden"):
    """Highlight forbidden characters in a text widget. Returns True if any found."""
    text_widget.tag_remove(tag_name, "1.0", tk.END)
    content = text_widget.get("1.0", tk.END).rstrip("\n")
    found = False
    for i, ch in enumerate(content):
        if not is_printable_ascii(ch):
            # Calculate tkinter text index (1-based line, 0-based col)
            line = content[:i].count("\n") + 1
            col = i - content[:i].rfind("\n") - 1
            start = f"{line}.{col}"
            end = f"{line}.{col + 1}"
            text_widget.tag_add(tag_name, start, end)
            found = True
    return found


def highlight_forbidden_key(tag_name="forbidden"):
    """Highlight forbidden characters in the key entry. Returns True if any found."""
    key_entry.config(bg="white")
    key = key_var.get()
    for ch in key:
        if not is_printable_ascii(ch):
            key_entry.config(bg="#ffcccc")
            return True
    return False


def clear_highlights():
    """Remove all error highlights and status message."""
    message_text.tag_remove("forbidden", "1.0", tk.END)
    cipher_text.tag_remove("forbidden", "1.0", tk.END)
    key_entry.config(bg="white")
    status_var.set("")


def show_status(msg, is_error=False):
    """Show a status message below the buttons."""
    status_var.set(msg)
    status_label.config(fg="#cc0000" if is_error else "#006600")


def on_encode():
    """Encode the message and display the ciphertext."""
    clear_highlights()
    key = key_var.get()

    if not key:
        show_status("Key must not be empty.", is_error=True)
        return

    if highlight_forbidden_key():
        show_status("Key contains forbidden characters (only ASCII 32-126 allowed).", is_error=True)
        return

    if highlight_forbidden(message_text):
        show_status("Message contains forbidden characters (highlighted in red). Only ASCII 32-126 allowed.", is_error=True)
        return

    message = message_text.get("1.0", tk.END).rstrip("\n")
    try:
        # Encode each line separately to preserve newlines
        lines = message.split("\n")
        result = "\n".join(encode(key, line) for line in lines)
        cipher_text.delete("1.0", tk.END)
        cipher_text.insert("1.0", result)
        show_status("Encoded successfully.")
    except (TypeError, ValueError) as err:
        show_status(str(err), is_error=True)


def on_decode():
    """Decode the ciphertext and display the message."""
    clear_highlights()
    key = key_var.get()

    if not key:
        show_status("Key must not be empty.", is_error=True)
        return

    if highlight_forbidden_key():
        show_status("Key contains forbidden characters (only ASCII 32-126 allowed).", is_error=True)
        return

    if highlight_forbidden(cipher_text):
        show_status("Ciphertext contains forbidden characters (highlighted in red). Only ASCII 32-126 allowed.", is_error=True)
        return

    ciphertext = cipher_text.get("1.0", tk.END).rstrip("\n")
    try:
        # Decode each line separately to preserve newlines
        lines = ciphertext.split("\n")
        result = "\n".join(decode(key, line) for line in lines)
        message_text.delete("1.0", tk.END)
        message_text.insert("1.0", result)
        show_status("Decoded successfully.")
    except (TypeError, ValueError) as err:
        show_status(str(err), is_error=True)


def on_clear():
    """Clear all fields."""
    clear_highlights()
    key_var.set("")
    message_text.delete("1.0", tk.END)
    cipher_text.delete("1.0", tk.END)


# --- Main window ---
root = tk.Tk()
root.title(f"MessageCipher v{VERSION}")
root.resizable(True, True)
root.minsize(500, 400)

# Configure grid weights for resizing
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(4, weight=1)

# --- Key field ---
tk.Label(root, text="Key:", font=("Segoe UI", 10)).grid(
    row=0, column=0, sticky="w", padx=10, pady=(10, 5)
)
key_frame = tk.Frame(root)
key_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=(10, 5))
key_frame.columnconfigure(0, weight=1)

key_var = tk.StringVar()
key_entry = tk.Entry(key_frame, textvariable=key_var, font=("Segoe UI", 10), show="*")
key_entry.grid(row=0, column=0, sticky="ew")


def toggle_key_visibility():
    if key_entry.cget("show") == "*":
        key_entry.config(show="")
        show_key_btn.config(text="\U0001f648")
    else:
        key_entry.config(show="*")
        show_key_btn.config(text="\U0001f441")


show_key_btn = tk.Button(key_frame, text="\U0001f441", command=toggle_key_visibility,
                         font=("Segoe UI", 9), width=3)
show_key_btn.grid(row=0, column=1, padx=(5, 0))

# --- Message field ---
tk.Label(root, text="Message:", font=("Segoe UI", 10)).grid(
    row=1, column=0, sticky="nw", padx=10, pady=5
)
message_text = tk.Text(root, font=("Consolas", 10), height=5, wrap=tk.WORD)
message_text.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
message_text.tag_configure("forbidden", background="#ff6666", foreground="white")

# --- Buttons ---
btn_frame = tk.Frame(root)
btn_frame.grid(row=2, column=0, columnspan=2, pady=5)

tk.Button(btn_frame, text="\u25bc Encode \u25bc", command=on_encode, width=14,
          font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="\u25b2 Decode \u25b2", command=on_decode, width=14,
          font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Clear", command=on_clear, width=10,
          font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)

# --- Status bar ---
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font=("Segoe UI", 9),
                        anchor="w")
status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10)

# --- Ciphertext field ---
tk.Label(root, text="Ciphertext:", font=("Segoe UI", 10)).grid(
    row=4, column=0, sticky="nw", padx=10, pady=5
)
cipher_text = tk.Text(root, font=("Consolas", 10), height=5, wrap=tk.WORD)
cipher_text.grid(row=4, column=1, sticky="nsew", padx=10, pady=(5, 10))
cipher_text.tag_configure("forbidden", background="#ff6666", foreground="white")

# --- Build info label ---
build_label = tk.Label(root, text=f"Build: {BUILD_TIMESTAMP}", font=("Segoe UI", 8),
                       anchor="w", fg="#666666")
build_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))

# --- Run ---
root.mainloop()
