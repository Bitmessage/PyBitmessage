#!/usr/bin/env python2.7
"""
setup.py
========

Install the pybitmessage package and dependencies.
"""

from __future__ import print_function

import os
import shutil

from setuptools import Extension, setup
from setuptools.command.install import install

from src.version import softwareVersion

EXTRAS_REQUIRE = {
    'gir': ['pygobject'],
    'notify2': ['notify2'],
    'pyopencl': ['pyopencl'],
    'prctl': ['python_prctl'],  # Named threads
    'qrcode': ['qrcode'],
    'sound;platform_system=="Windows"': ['winsound'],
    'devops': [
        'autopep8',  # fab code_quality
        'fabric==1.14.0',
        'fabric-virtualenv',
        'flake8==3.4.1',  # https://github.com/PyCQA/pycodestyle/issues/741
        'graphviz',  # fab build_docs
        'isort',  # fab code_quality
        'm2r',  # fab build_docs
        'pycodestyle==2.3.1',  # https://github.com/PyCQA/pycodestyle/issues/741
        'pylint',  # fab code_quality
        'python2-pythondialog',  # src/depends.py
        'sphinx',  # fab build_docs
    ],
}


class InstallCmd(install):
    """Install PyBitmessage"""

    def run(self):
        # prepare icons directories
        try:
            os.makedirs('desktop/icons/scalable')
        except os.error:
            pass
        shutil.copyfile(
            'desktop/can-icon.svg', 'desktop/icons/scalable/pybitmessage.svg')
        try:
            os.makedirs('desktop/icons/24x24')
        except os.error:
            pass
        shutil.copyfile(
            'desktop/icon24.png', 'desktop/icons/24x24/pybitmessage.png')

        return install.run(self)


if __name__ == "__main__":

    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()

    bitmsghash = Extension(
        'pybitmessage.bitmsghash.bitmsghash',
        sources=['src/bitmsghash/bitmsghash.cpp'],
        libraries=['pthread', 'crypto'],
    )

    installRequires = []
    packages = [
        'pybitmessage',
        'pybitmessage.bitmessageqt',
        'pybitmessage.bitmessagecurses',
        'pybitmessage.messagetypes',
        'pybitmessage.network',
        'pybitmessage.plugins',
        'pybitmessage.pyelliptic',
        'pybitmessage.socks',
        'pybitmessage.storage',
    ]

    # this will silently accept alternative providers of msgpack
    # if they are already installed

    try:
        import msgpack  # pylint: disable=unused-import
        installRequires.append("msgpack-python")
    except ImportError:
        try:
            import umsgpack  # pylint: disable=unused-import
            installRequires.append("umsgpack")
        except ImportError:
            packages += ['pybitmessage.fallback', 'pybitmessage.fallback.umsgpack']

    dist = setup(
        name='pybitmessage',
        version=softwareVersion,
        description="Reference client for Bitmessage: "
        "a P2P communications protocol",
        long_description=README,
        license='MIT',
        author='The Bitmessage Team',
        author_email='surda@economicsofbitcoin.com',
        url='https://bitmessage.org',
        keywords='bitmessage pybitmessage',
        install_requires=installRequires,
        extras_require=EXTRAS_REQUIRE,
        classifiers=[
            "License :: OSI Approved :: MIT License"
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7 :: Only",
            "Topic :: Internet",
            "Topic :: Security :: Cryptography",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        package_dir={'pybitmessage': 'src'},
        packages=packages,
        package_data={'': [
            'bitmessageqt/*.ui', 'bitmsghash/*.cl', 'sslkeys/*.pem',
            'translations/*.ts', 'translations/*.qm',
            'images/*.png', 'images/*.ico', 'images/*.icns'
        ]},
        data_files=[
            ('share/applications/',
             ['desktop/pybitmessage.desktop']),
            ('share/icons/hicolor/scalable/apps/',
             ['desktop/icons/scalable/pybitmessage.svg']),
            ('share/icons/hicolor/24x24/apps/',
             ['desktop/icons/24x24/pybitmessage.png'])
        ],
        ext_modules=[bitmsghash],
        zip_safe=False,
        entry_points={
            'bitmessage.gui.menu': [
                'address.qrcode = pybitmessage.plugins.menu_qrcode [qrcode]'
            ],
            'bitmessage.notification.message': [
                'notify2 = pybitmessage.plugins.notification_notify2'
                '[gir, notify2]'
            ],
            'bitmessage.notification.sound': [
                'theme.canberra = pybitmessage.plugins.sound_canberra',
                'file.gstreamer = pybitmessage.plugins.sound_gstreamer'
                '[gir]',
                'file.fallback = pybitmessage.plugins.sound_playfile'
                '[sound]'
            ],
            'bitmessage.indicator': [
                'libmessaging ='
                'pybitmessage.plugins.indicator_libmessaging [gir]'
            ],
        },
        scripts=['src/pybitmessage'],
        cmdclass={'install': InstallCmd}
    )
