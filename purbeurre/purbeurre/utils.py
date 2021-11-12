from typing import Any


def strtobool(val: Any) -> bool:
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    Args:
        val: The string that will be analysed.

    Returns:
        The boolean value corresponding to the string value.
    """
    if isinstance(val, str):
        return val.lower() in ('y', 'yes', 't', 'true', 'on', '1')

    return bool(val)
