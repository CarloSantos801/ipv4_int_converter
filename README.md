# IPv4 Int Converter

Convert IPv4 addresses between dotted-quad strings (`"192.0.2.1"`) and unsigned 32-bit integers (`3221225985`).

## Usage

```python
from ipv4_int_converter import ip_to_int, int_to_ip, IpConversionError

ip_to_int("192.0.2.1")        # -> 3221225985
int_to_ip(3221225985)         # -> "192.0.2.1"

try:
    ip_to_int("256.0.0.1")
except IpConversionError as exc:
    print(exc)  # octet out of range (0-255): 256
```

Install with `PYTHONPATH=src` on your environment, or drop `src/ipv4_int_converter` onto `sys.path`.

## Why this exists

Some databases and APIs store IPv4 addresses as unsigned 32-bit integers. The standard library's `socket.inet_aton`/`inet_ntoa` round-trip through byte strings, which is fine until you need a plain `int` for indexing, arithmetic, or storage in a column that is genuinely numeric. This library gives you that one conversion with no ceremony and no third-party dependencies.

The trade-off: the integer is treated as **unsigned**. `int_to_ip(-1)` raises rather than returning `"255.255.255.255"`. If you are dealing with values that might be the two's-complement representation of a negative signed 32-bit int from another system, mask to unsigned (`value & 0xFFFFFFFF`) before calling `int_to_ip`. That decision is made once, here, so every caller sees the same rule.

## Awkward edges

- **Leading zeros in octets are accepted.** `"010.0.0.1"` is parsed as decimal `10`, not octal `8`. Dotted-quad notation has no octal semantics, so `"0.0.0.0"` itself has a leading zero and we don't reject it.
- **Booleans are rejected** by `int_to_ip`, even though `bool` is a subclass of `int` in Python. Passing `True` almost always means you called the wrong function.
- `IpConversionError` is a subclass of `ValueError`, so existing `except ValueError` handlers still catch it.
