import unittest

from ipv4_int_converter import ip_to_int, int_to_ip, IpConversionError


class IpToIntTests(unittest.TestCase):

    def test_zero_address(self):
        self.assertEqual(ip_to_int("0.0.0.0"), 0)

    def test_max_address(self):
        self.assertEqual(ip_to_int("255.255.255.255"), 4294967295)

    def test_standard_example(self):
        self.assertEqual(ip_to_int("192.0.2.1"), 0xC0000201)

    def test_octet_order(self):
        # 1.2.3.4 -> 0x01020304; verifies octet 0 is most significant.
        self.assertEqual(ip_to_int("1.2.3.4"), 0x01020304)

    def test_leading_zero_in_octet_allowed(self):
        # Dotted-quad has no octal semantics; "010" is decimal 10.
        self.assertEqual(ip_to_int("010.0.0.1"), 0x0A000001)

    def test_rejects_non_string(self):
        with self.assertRaises(IpConversionError):
            ip_to_int(3221225985)

    def test_rejects_too_few_octets(self):
        with self.assertRaises(IpConversionError):
            ip_to_int("192.0.2")

    def test_rejects_too_many_octets(self):
        with self.assertRaises(IpConversionError):
            ip_to_int("192.0.2.1.5")

    def test_rejects_empty_octet(self):
        with self.assertRaises(IpConversionError):
            ip_to_int("192..2.1")

    def test_rejects_out_of_range_octet(self):
        with self.assertRaises(IpConversionError):
            ip_to_int("256.0.0.1")

    def test_rejects_negative_octet_literal(self):
        with self.assertRaises(IpConversionError):
            ip_to_int("-1.0.0.1")

    def test_rejects_hex_octet(self):
        with self.assertRaises(IpConversionError):
            ip_to_int("0x1.0.0.1")


class IntToIpTests(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(int_to_ip(0), "0.0.0.0")

    def test_max(self):
        self.assertEqual(int_to_ip(4294967295), "255.255.255.255")

    def test_standard_example(self):
        self.assertEqual(int_to_ip(0xC0000201), "192.0.2.1")

    def test_canonical_no_leading_zeros(self):
        self.assertEqual(int_to_ip(0x0A000001), "10.0.0.1")

    def test_rejects_negative(self):
        with self.assertRaises(IpConversionError):
            int_to_ip(-1)

    def test_rejects_overflow(self):
        with self.assertRaises(IpConversionError):
            int_to_ip(4294967296)

    def test_rejects_bool(self):
        with self.assertRaises(IpConversionError):
            int_to_ip(True)

    def test_rejects_non_int(self):
        with self.assertRaises(IpConversionError):
            int_to_ip("3221225985")


class RoundTripTests(unittest.TestCase):

    def test_round_trip_all_corner_addresses(self):
        for s in ("0.0.0.0", "255.255.255.255", "127.0.0.1", "10.0.0.1"):
            self.assertEqual(int_to_ip(ip_to_int(s)), s)


if __name__ == "__main__":
    unittest.main()
