import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt'), encoding='utf-8') as f:
    CHANGES = f.read()


setup(
    name='pybitmessage',
    version='0.6',
    description='',
    long_description=README,
    license='MIT',
    # TODO: add author info
    #author='',
    #author_email='',
    url='https://github.com/Bitmessage/PyBitmessage/',
    # TODO: add keywords
    #keywords='',
    install_requires = ['hashlib', 'sqlite3', 'ctypes', 'curses', 'dialog', 'PyQt4', 'msgpack-python'],
    classifiers = [
        "License :: OSI Approved :: MIT License"
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7.3",
        "Programming Language :: Python :: 2.7.4",
        "Programming Language :: Python :: 2.7.5",
        "Programming Language :: Python :: 2.7.6",
        "Programming Language :: Python :: 2.7.7",
        "Programming Language :: Python :: 2.7.8",
        "Programming Language :: Python :: 2.7.9",
        "Programming Language :: Python :: 2.7.10",
        "Programming Language :: Python :: 2.7.11",
        "Programming Language :: Python :: 2.7.12",
        "Programming Language :: Python :: 2.7.13",
    ],
    packages=find_packages(include=['src'])
    include_package_data=True,
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    bitmessage = src.bitmessagemain:Main.start
    """,
)
