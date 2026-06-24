"""Pre-build script to auto-increment the application version and stamp the build timestamp."""

import sys
import re
from datetime import datetime, timezone
from pathlib import Path


VERSION_FILE = Path(__file__).parent / "version.py"

VERSION_PATTERN = re.compile(r'^VERSION:\s*str\s*=\s*"(\d+\.\d+)"', re.MULTILINE)
TIMESTAMP_PATTERN = re.compile(r'^BUILD_TIMESTAMP:\s*str\s*=\s*"(.*?)"', re.MULTILINE)


def read_current_version(content: str) -> tuple[int, int]:
    """Extract and parse the current VERSION from version.py content.

    Args:
        content: The full text content of version.py.

    Returns:
        A tuple (major, minor) of the current version.

    Exits:
        Prints error to stderr and calls sys.exit(1) if VERSION line
        cannot be found or parsed.
    """
    match = VERSION_PATTERN.search(content)
    if not match:
        print(
            "Error: version.py is missing or has malformed VERSION",
            file=sys.stderr,
        )
        sys.exit(1)

    version_str = match.group(1)
    parts = version_str.split(".")
    if len(parts) != 2:
        print(
            "Error: version.py is missing or has malformed VERSION",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        major = int(parts[0])
        minor = int(parts[1])
    except ValueError:
        print(
            "Error: version.py is missing or has malformed VERSION",
            file=sys.stderr,
        )
        sys.exit(1)

    return (major, minor)


def bump_minor(major: int, minor: int) -> str:
    """Increment minor version by 1, return formatted version string.

    Args:
        major: Current major version.
        minor: Current minor version.

    Returns:
        New version string with minor incremented.
    """
    return f"{major}.{minor + 1}"


def generate_timestamp() -> str:
    """Generate the current UTC timestamp in ISO 8601 format.

    Returns:
        String in "YYYY-MM-DDTHH:MM:SSZ" format.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def update_version_file(file_path: Path) -> None:
    """Read version.py, bump version, write back.

    Reads the file, increments the minor version, sets the build timestamp
    to now, and overwrites the file.

    Args:
        file_path: Path to version.py.

    Exits:
        Prints error to stderr and calls sys.exit(1) if the file is missing
        or the version format is invalid.
    """
    if not file_path.exists():
        print(
            "Error: version.py is missing or has malformed VERSION",
            file=sys.stderr,
        )
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")

    major, minor = read_current_version(content)
    new_version = bump_minor(major, minor)
    new_timestamp = generate_timestamp()

    # Replace VERSION line
    content = VERSION_PATTERN.sub(
        f'VERSION: str = "{new_version}"', content
    )
    # Replace BUILD_TIMESTAMP line
    content = TIMESTAMP_PATTERN.sub(
        f'BUILD_TIMESTAMP: str = "{new_timestamp}"', content
    )

    file_path.write_text(content, encoding="utf-8")
    print(f"Version bumped to {new_version} (build: {new_timestamp})")


def main() -> None:
    """Entry point for the bump script."""
    update_version_file(VERSION_FILE)


if __name__ == "__main__":
    main()
