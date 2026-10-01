"""Convert IPv4 addresses between dotted-quad and 32-bit integers.

Design decisions, stated plainly so the behaviour is not a surprise:

* Each decimal octet must be in the canonical range 0-255. A leading "0" is
  *allowed* because the dotted-quad form has no ambiguity (unlike C-style
  octal literals), and "0.0.0.0" itself has a leading zero. What we reject is
  a value outside the numeric range.
* A bare integer must fit in an unsigned 32-bit range: 0 <= n <= 2**32 - 1.
  Signed interpretations are not supported; the caller is expected to pass an
  unsigned value.
* The integer is treated as unsigned, and int_to_ip returns the canonical
  dotted-quad form (four octets, no leading zeros within an octet). If you
  need a network-order byte string, use socket.inet_aton directly.
* Negative integers are rejected, not silently reinterpreted as their
  two's complement unsigned counterpart. That reinterpretation is a genuine
  source of bugs in network code and we will not paper over it.
"""


class IpConversionError(ValueError):
    """Raised when an input is not a valid IPv4 address or 32-bit integer.

    Subclassing ValueError lets callers catch the specific failure without
    losing the familiar ValueError semantics they may already handle.
    """


_MAX_OCTET = 255
_UINT32_MAX = (1 << 32) - 1


def _parse_octet(raw: str) -> int:
    if not raw:
        raise IpConversionError("empty octet")
    # str.isdigit() rejects signs, spaces, and non-ASCII digits such as the
    # Arabic-Indic numerals. Decimal-only is what dotted-quad means.
    if not raw.isdigit():
        raise IpConversionError(f"octet is not a non-negative decimal integer: {raw!r}")
    value = int(raw)
    if value > _MAX_OCTET:
        raise IpConversionError(f"octet out of range (0-255): {value}")
    return value


def ip_to_int(address):
    """Convert a dotted-quad IPv4 string to its unsigned 32-bit integer.

    Args:
        address: A string like "192.0.2.1".

    Returns:
        int: The address as an unsigned 32-bit integer (e.g. 3221225985).

    Raises:
        IpConversionError: If the input is not a string, does not have exactly
            four octets, or an octet is not a decimal integer in 0-255.
    """
    if not isinstance(address, str):
        raise IpConversionError(
            f"address must be a dotted-quad string, got {type(address).__name__}"
        )
    parts = address.split(".")
    if len(parts) != 4:
        raise IpConversionError(
            f"address must have exactly four octets, got {len(parts)}"
        )
    result = 0
    for i, part in enumerate(parts):
        octet = _parse_octet(part)
        # Most-significant octet first, as on the wire for humans.
        result |= octet << (24 - 8 * i)
    return result


def int_to_ip(value):
    """Convert an unsigned 32-bit integer to a dotted-quad IPv4 string.

    Args:
        value: An int in the range 0..4294967295.

    Returns:
        str: The canonical dotted-quad form, e.g. "192.0.2.1".

    Raises:
        IpConversionError: If the input is not an int or is outside the
            unsigned 32-bit range.
    """
    # bool is a subclass of int in Python. Accepting True/False would silently
    # produce 0.0.0.1 / 0.0.0.0, which is almost never what the caller meant.
    if isinstance(value, bool) or not isinstance(value, int):
        raise IpConversionError(
            f"value must be an int in 0..{ _UINT32_MAX }, got {type(value).__name__}"
        )
    if value < 0 or value > _UINT32_MAX:
        raise IpConversionError(
            f"value out of range (0..{ _UINT32_MAX }): {value}"
        )
    octets = [
        str((value >> shift) & 0xFF)
        for shift in (24, 16, 8, 0)
    ]
    return ".".join(octets)
