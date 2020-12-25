#!/usr/bin/env python2.7

import os
import platform
import shutil
import sys

from setuptools import setup, Extension
from setuptools.command.install import install

from src.version import softwareVersion


EXTRAS_REQUIRE = {
    'gir': ['pygobject'],
    'json': ['jsonrpclib'],
    'notify2': ['notify2'],
    'opencl': ['pyopencl', 'numpy'],
    'prctl': ['python_prctl'],  # Named threads
    'qrcode': ['qrcode'],
    'sound;platform_system=="Windows"': ['winsound'],
    'tor': ['stem'],
    'xml': ['defusedxml'],
    'docs': ['sphinx', 'sphinxcontrib-apidoc', 'm2r']
}

if sys.version_info[0] == 2:
    version_dependencies = {
        'requirements_file': 'requirements.txt',
        'pybitmessage_file': 'src/pybitmessage'
    }
else:
    version_dependencies = {
        'requirements_file': 'py3_requirements.txt',
        'pybitmessage_file': 'src/py3_pybitmessage'
    }


class InstallCmd(install):
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

    with open(os.path.join(here, version_dependencies['requirements_file']), 'r') as f:
        requirements = list(f.readlines())

    bitmsghash = Extension(
        'pybitmessage.bitmsghash.bitmsghash',
        sources=['src/bitmsghash/bitmsghash.cpp'],
        libraries=['pthread', 'crypto'],
    )

    installRequires = []
    packages = [
        'pybitmessage',
        # 'pybitmessage.bitmessageqt',
        # 'pybitmessage.bitmessagecurses',
        'pybitmessage.fallback',
        'pybitmessage.messagetypes',
        'pybitmessage.network',
        'pybitmessage.plugins',
        'pybitmessage.pyelliptic',
        'pybitmessage.storage'
    ]

    # this will silently accept alternative providers of msgpack
    # if they are already installed

    try:
        import msgpack
        installRequires.append(
            "msgpack-python" if msgpack.version[:2] == (0, 4) else "msgpack")
    except ImportError:
        try:
            installRequires.append("umsgpack")
        except ImportError:
            packages += ['pybitmessage.fallback.umsgpack']

    data_files = [
        ('share/applications/',
            ['desktop/pybitmessage.desktop']),
        ('share/icons/hicolor/scalable/apps/',
            ['desktop/icons/scalable/pybitmessage.svg']),
        ('share/icons/hicolor/24x24/apps/',
            ['desktop/icons/24x24/pybitmessage.png'])
    ]

    if platform.dist()[0] in ('Debian', 'Ubuntu'):
        data_files += [
            ("etc/apparmor.d/",
                ['packages/apparmor/pybitmessage'])
        ]

    dist = setup(
        name='pybitmessage',
        version=softwareVersion,
        description="Reference client for Bitmessage: "
        "a P2P communications protocol",
        long_description=README,
        license='MIT',
        # TODO: add author info
        # author='',
        # author_email='',
        url='https://bitmessage.org',
        # TODO: add keywords
        # keywords='',
        install_requires=installRequires,
        tests_require=requirements,
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
            'sslkeys/*.pem',
            'translations/*.ts', 'translations/*.qm',
            'images/*.png', 'images/*.ico', 'images/*.icns'
        ]},
        data_files=data_files,
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
            'bitmessage.proxyconfig': [
                'stem = pybitmessage.plugins.proxyconfig_stem [tor]'
            ],
            'console_scripts': [
                'pybitmessage = pybitmessage.bitmessagemain:main'
            ] if sys.platform[:3] == 'win' else []
        },
        scripts=[version_dependencies['pybitmessage_file']],
        cmdclass={'install': InstallCmd},
        command_options={
            'build_sphinx': {
                'source_dir': ('setup.py', 'docs')}
        }
    )
