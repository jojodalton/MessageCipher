"""Shared test fixtures and configuration for message_cipher tests."""

import sys
import os

# Ensure the project root is on the path so `import message_cipher` works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
