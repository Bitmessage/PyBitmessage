import sys

if getattr(sys, 'frozen', None):
    from test_addresses import TestAddresses
    from test_crypto import TestHighlevelcrypto
    from test_l10n import TestL10n
    from test_packets import TestSerialize
    from test_protocol import TestProtocol

    __all__ = [
        "TestAddresses", "TestHighlevelcrypto", "TestL10n",
        "TestProtocol", "TestSerialize"
    ]
