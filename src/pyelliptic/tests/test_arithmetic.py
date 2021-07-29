"""
Test the arithmetic functions
"""

from binascii import unhexlify
import unittest

try:
    from pyelliptic import arithmetic
except ImportError:
    from pybitmessage.pyelliptic import arithmetic


# These keys are from addresses test script
sample_pubsigningkey = (
    b'044a367f049ec16cb6b6118eb734a9962d10b8db59c890cd08f210c43ff08bdf09d'
    b'16f502ca26cd0713f38988a1237f1fc8fa07b15653c996dc4013af6d15505ce')
sample_pubencryptionkey = (
    b'044597d59177fc1d89555d38915f581b5ff2286b39d022ca0283d2bdd5c36be5d3c'
    b'e7b9b97792327851a562752e4b79475d1f51f5a71352482b241227f45ed36a9')
sample_privsigningkey = \
    b'93d0b61371a54b53df143b954035d612f8efa8a3ed1cf842c2186bfd8f876665'
sample_privencryptionkey = \
    b'4b0b73a54e19b059dc274ab69df095fe699f43b17397bca26fdf40f4d7400a3a'

# [chan] bitmessage
sample_wif_privsigningkey = \
    b'a2e8b841a531c1c558ee0680c396789c7a2ea3ac4795ae3f000caf9fe367d144'
sample_wif_privencryptionkey = \
    b'114ec0e2dca24a826a0eed064b0405b0ac148abc3b1d52729697f4d7b873fdc6'

sample_factor = \
    66858749573256452658262553961707680376751171096153613379801854825275240965733
# G * sample_factor
sample_point = (
    33567437183004486938355437500683826356288335339807546987348409590129959362313,
    94730058721143827257669456336351159718085716196507891067256111928318063085006
)


class TestArithmetic(unittest.TestCase):
    """Test arithmetic functions"""
    def test_base10_multiply(self):
        """Test arithmetic.base10_multiply"""
        self.assertEqual(
            sample_point,
            arithmetic.base10_multiply(arithmetic.G, sample_factor))

    def test_base58(self):
        """Test encoding/decoding base58 using arithmetic functions"""
        self.assertEqual(
            arithmetic.decode(arithmetic.changebase(
                b'2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK', 58, 256), 256),
            25152821841976547050350277460563089811513157529113201589004)
        self.assertEqual(
            arithmetic.decode(arithmetic.changebase(
                b'2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN', 58, 256), 256),
            18875720106589866286514488037355423395410802084648916523381)
        self.assertEqual(
            arithmetic.changebase(arithmetic.encode(
                25152821841976547050350277460563089811513157529113201589004,
                256), 256, 58), b'2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK')
        self.assertEqual(
            arithmetic.changebase(arithmetic.encode(
                18875720106589866286514488037355423395410802084648916523381,
                256), 256, 58), b'2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN')

    def test_wif(self):
        """Decode WIFs of [chan] bitmessage and check the keys"""
        self.assertEqual(
            sample_wif_privsigningkey,
            arithmetic.changebase(arithmetic.changebase(
                b'5K42shDERM5g7Kbi3JT5vsAWpXMqRhWZpX835M2pdSoqQQpJMYm', 58, 256
            )[1:-4], 256, 16))
        self.assertEqual(
            sample_wif_privencryptionkey,
            arithmetic.changebase(arithmetic.changebase(
                b'5HwugVWm31gnxtoYcvcK7oywH2ezYTh6Y4tzRxsndAeMi6NHqpA', 58, 256
            )[1:-4], 256, 16))

    def test_decode(self):
        """Decode sample privsigningkey from hex to int and compare to factor"""
        self.assertEqual(
            arithmetic.decode(sample_privsigningkey, 16), sample_factor)

    def test_encode(self):
        """Encode sample factor into hex and compare to privsigningkey"""
        self.assertEqual(
            arithmetic.encode(sample_factor, 16), sample_privsigningkey)

    def test_changebase(self):
        """Check the results of changebase()"""
        self.assertEqual(
            arithmetic.changebase(sample_privsigningkey, 16, 256, minlen=32),
            unhexlify(sample_privsigningkey))
        self.assertEqual(
            arithmetic.changebase(sample_pubsigningkey, 16, 256, minlen=64),
            unhexlify(sample_pubsigningkey))
        self.assertEqual(
            32,  # padding
            len(arithmetic.changebase(sample_privsigningkey[:5], 16, 256, 32)))

    def test_hex_to_point(self):
        """Check that sample_pubsigningkey is sample_point encoded in hex"""
        self.assertEqual(
            arithmetic.hex_to_point(sample_pubsigningkey), sample_point)

    def test_point_to_hex(self):
        """Check that sample_point is sample_pubsigningkey decoded from hex"""
        self.assertEqual(
            arithmetic.point_to_hex(sample_point), sample_pubsigningkey)

    def test_privtopub(self):
        """Generate public keys and check the result"""
        self.assertEqual(
            arithmetic.privtopub(sample_privsigningkey),
            sample_pubsigningkey
        )
        self.assertEqual(
            arithmetic.privtopub(sample_privencryptionkey),
            sample_pubencryptionkey
        )
