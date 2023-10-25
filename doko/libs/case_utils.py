"""
Helper functions to change cases of strings.
"""

import re


def camel_to_snake(name: str) -> str:
    """Transform a string from CamelCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
