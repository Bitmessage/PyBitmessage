import os
from setuptools import setup

name = "Bitmessage"
version = os.getenv("PYBITMESSAGEVERSION", "custom")
mainscript = ["bitmessagemain.py"]

setup(
    name = name,
    version = version,
    app = mainscript,
    setup_requires = ["py2app"],
    options = dict(
        py2app = dict(
            resources = ["images", "translations", "bitmsghash", "sslkeys"],
            includes = ['sip', 'PyQt4._qt'],
            iconfile = "images/bitmessage.icns"
        )
    )
)
