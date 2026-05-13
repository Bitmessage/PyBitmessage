"""bitmessageqt tests"""

from .addressbook import TestAddressbook
from .main import TestMain, TestUISignaler
from .settings import TestSettings
from .support import TestSupport
from .test_import import TestImports
from .test_startup import TestStartup
from .test_widgets import (
    TestAddressValidator, TestLanguageBox, TestMessageView,
    TestSafeHTMLParser
)

__all__ = [
    "TestAddressbook", "TestAddressValidator", "TestLanguageBox",
    "TestImports", "TestMain", "TestMessageView", "TestSafeHTMLParser",
    "TestSettings", "TestStartup", "TestSupport", "TestUISignaler"
]
