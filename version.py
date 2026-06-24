"""Version information for the MessageCipher application."""

VERSION: str = "0.3"
BUILD_TIMESTAMP: str = "2026-06-23T14:31:14Z"


def parse_version(version_str: str) -> tuple[int, int]:
    """Parse a version string into (major, minor) integers.

    Args:
        version_str: A string in "MAJOR.MINOR" format.

    Returns:
        A tuple (major, minor) of non-negative integers.

    Raises:
        ValueError: If the string does not match "MAJOR.MINOR" format,
                    contains non-integer parts, negative numbers, or leading zeros.
    """
    if not isinstance(version_str, str):
        raise ValueError(f"Invalid version format: expected a string, got {type(version_str).__name__}")

    parts = version_str.split(".")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid version format: '{version_str}'. Expected 'MAJOR.MINOR' with exactly one dot."
        )

    major_str, minor_str = parts

    # Validate that both parts are non-empty
    if not major_str or not minor_str:
        raise ValueError(
            f"Invalid version format: '{version_str}'. MAJOR and MINOR must not be empty."
        )

    # Validate that both parts contain only digits (no negative signs, spaces, etc.)
    if not major_str.isdigit() or not minor_str.isdigit():
        raise ValueError(
            f"Invalid version format: '{version_str}'. MAJOR and MINOR must be non-negative integers."
        )

    # Check for leading zeros (except single "0")
    if len(major_str) > 1 and major_str[0] == "0":
        raise ValueError(
            f"Invalid version format: '{version_str}'. MAJOR must not have leading zeros."
        )
    if len(minor_str) > 1 and minor_str[0] == "0":
        raise ValueError(
            f"Invalid version format: '{version_str}'. MINOR must not have leading zeros."
        )

    major = int(major_str)
    minor = int(minor_str)

    return (major, minor)


def format_version(major: int, minor: int) -> str:
    """Format major and minor integers into a version string.

    Args:
        major: Non-negative integer for the major component.
        minor: Non-negative integer for the minor component.

    Returns:
        A string in "MAJOR.MINOR" format with no leading zeros.

    Raises:
        ValueError: If major or minor is negative.
    """
    if major < 0:
        raise ValueError(f"Invalid version: major must be non-negative, got {major}.")
    if minor < 0:
        raise ValueError(f"Invalid version: minor must be non-negative, got {minor}.")

    return f"{major}.{minor}"


def compare_versions(v1: str, v2: str) -> int:
    """Compare two version strings numerically.

    Args:
        v1: First version string in "MAJOR.MINOR" format.
        v2: Second version string in "MAJOR.MINOR" format.

    Returns:
        -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2.

    Raises:
        ValueError: If either string is not a valid version format.
    """
    parsed_v1 = parse_version(v1)
    parsed_v2 = parse_version(v2)

    if parsed_v1 < parsed_v2:
        return -1
    elif parsed_v1 == parsed_v2:
        return 0
    else:
        return 1


def validate_version(version_str: str) -> bool:
    """Check whether a string is a valid version format.

    A valid version is "MAJOR.MINOR" where both parts are non-negative
    integers with no leading zeros (except the single digit "0").

    Args:
        version_str: The string to validate.

    Returns:
        True if valid.

    Raises:
        ValueError: If the format is invalid, with a descriptive message.
    """
    parse_version(version_str)
    return True
