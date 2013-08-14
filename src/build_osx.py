from setuptools import setup

name = "Bitmessage"
version = "0.3.4"
mainscript = ["bitmessagemain.py"]

setup(
     name = name,
	version = version,
	app = mainscript,
	setup_requires = ["py2app"],
	options = dict(py2app=dict(
		resources = ["images"],
		iconfile = "images/bitmessage.icns"
    ))
)
