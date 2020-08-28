#!/bin/bash

# INIT
MACHINE_TYPE=$(uname -m)
BASE_DIR=$(pwd)
PYTHON_VERSION=2.7.17
PYQT_VERSION=4-4.11.4-gpl-Py2.7-Qt4.8.7
OPENSSL_VERSION=1_0_2t
SRCPATH=~/Downloads

#Functions
function download_sources_32 {
	if [ ! -d ${SRCPATH} ]; then
		mkdir -p ${SRCPATH}
	fi
	wget -P ${SRCPATH} -c -nc --content-disposition \
		https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}.msi \
		https://download.microsoft.com/download/1/1/1/1116b75a-9ec3-481a-a3c8-1777b5381140/vcredist_x86.exe \
		https://github.com/Bitmessage/ThirdPartyLibraries/blob/master/PyQt${PYQT_VERSION}-x32.exe?raw=true \
		https://github.com/Bitmessage/ThirdPartyLibraries/blob/master/Win32OpenSSL-${OPENSSL_VERSION}.exe?raw=true \
		https://github.com/Bitmessage/ThirdPartyLibraries/blob/master/pyopencl-2015.1-cp27-none-win32.whl?raw=true
}

function download_sources_64 {
	if [ ! -d ${SRCPATH} ]; then
		mkdir -p ${SRCPATH}
	fi
	wget -P ${SRCPATH} -c -nc --content-disposition \
		http://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}.amd64.msi \
		https://download.microsoft.com/download/d/2/4/d242c3fb-da5a-4542-ad66-f9661d0a8d19/vcredist_x64.exe \
		https://github.com/Bitmessage/ThirdPartyLibraries/blob/master/PyQt${PYQT_VERSION}-x64.exe?raw=true \
		https://github.com/Bitmessage/ThirdPartyLibraries/blob/master/Win64OpenSSL-${OPENSSL_VERSION}.exe?raw=true \
		https://github.com/Bitmessage/ThirdPartyLibraries/blob/master/pyopencl-2015.1-cp27-none-win_amd64.whl?raw=true
}

function download_sources {
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
		download_sources_64
	else
		download_sources_32
	fi
}

function install_wine {
	echo "Setting up wine"
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
		export WINEPREFIX=${HOME}/.wine64 WINEARCH=win64
	else
		export WINEPREFIX=${HOME}/.wine32 WINEARCH=win32
	fi
	rm -rf "${WINEPREFIX}"
	rm -rf packages/pyinstaller/{build,dist}
}

function install_python(){
	cd ${SRCPATH} || exit 1
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
		echo "Installing Python ${PYTHON_VERSION} 64b"
		wine msiexec -i python-${PYTHON_VERSION}.amd64.msi /q /norestart
		echo "Installing vcredist for 64 bit"
		wine vcredist_x64.exe /q /norestart
	else
		echo "Installing Python ${PYTHON_VERSION} 32b"
		wine msiexec -i python-${PYTHON_VERSION}.msi /q /norestart
		# MSVCR 2008 required for Windows XP
		cd ${SRCPATH} || exit 1
		echo "Installing vc_redist (2008) for 32 bit "
		wine vcredist_x86.exe /Q
	fi
        echo "Installing pytools 2020.2"
        # last version compatible with python 2
        wine python -m pip install pytools==2020.2
	echo "Upgrading pip"
	wine python -m pip install --upgrade pip
}

function install_pyqt(){
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
		echo "Installing PyQt-${PYQT_VERSION} 64b"
		wine PyQt${PYQT_VERSION}-x64.exe /S /WX
	else
		echo "Installing PyQt-${PYQT_VERSION} 32b"
		wine PyQt${PYQT_VERSION}-x32.exe /S /WX
	fi
}

function install_openssl(){
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
		echo "Installing OpenSSL ${OPENSSL_VERSION} 64b"
		wine Win64OpenSSL-${OPENSSL_VERSION}.exe  /q /norestart /silent /verysilent /sp- /suppressmsgboxes
	else
		echo "Installing OpenSSL ${OPENSSL_VERSION} 32b"
		wine Win32OpenSSL-${OPENSSL_VERSION}.exe  /q /norestart /silent /verysilent /sp- /suppressmsgboxes
	fi
}

function install_pyinstaller()
{
	cd "${BASE_DIR}" || exit 1
	echo "Installing PyInstaller"
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
                # 3.6 is the last version to support python 2.7
		wine python -m pip install -I pyinstaller==3.6
	else
		# 3.2.1 is the last version to work on XP
		# see https://github.com/pyinstaller/pyinstaller/issues/2931
		wine python -m pip install -I pyinstaller==3.2.1
	fi
}

function install_msgpack()
{
	cd "${BASE_DIR}" || exit 1
	echo "Installing msgpack"
	wine python -m pip install msgpack-python
}

function install_pyopencl()
{
	cd "${SRCPATH}" || exit 1
	echo "Installing PyOpenCL"
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
		wine python -m pip install pyopencl-2015.1-cp27-none-win_amd64.whl
	else
		wine python -m pip install pyopencl-2015.1-cp27-none-win32.whl
	fi
        sed -Ei 's/_DEFAULT_INCLUDE_OPTIONS = .*/_DEFAULT_INCLUDE_OPTIONS = [] /' \
            "$WINEPREFIX/drive_c/Python27/Lib/site-packages/pyopencl/__init__.py"
}

function build_dll(){
	cd "${BASE_DIR}" || exit 1
	cd src/bitmsghash || exit 1
	if [ "${MACHINE_TYPE}" == 'x86_64' ]; then
		echo "Create dll"
		x86_64-w64-mingw32-g++ -D_WIN32 -Wall -O3 -march=native \
                    "-I$HOME/.wine64/drive_c/OpenSSL-Win64/include" \
                    -I/usr/x86_64-w64-mingw32/include \
                    "-L$HOME/.wine64/drive_c/OpenSSL-Win64/lib" \
                    -c bitmsghash.cpp
		x86_64-w64-mingw32-g++ -static-libgcc -shared bitmsghash.o \
                    -D_WIN32 -O3 -march=native \
                    "-I$HOME/.wine64/drive_c/OpenSSL-Win64/include" \
                    "-L$HOME/.wine64/drive_c/OpenSSL-Win64" \
                    -L/usr/lib/x86_64-linux-gnu/wine \
                    -fPIC -shared -lcrypt32 -leay32 -lwsock32 \
                    -o bitmsghash64.dll -Wl,--out-implib,bitmsghash.a
	else
		echo "Create dll"
		i686-w64-mingw32-g++ -D_WIN32 -Wall -m32 -O3 -march=native \
                    "-I$HOME/.wine32/drive_c/OpenSSL-Win32/include" \
                    -I/usr/i686-w64-mingw32/include \
                    "-L$HOME/.wine32/drive_c/OpenSSL-Win32/lib" \
                    -c bitmsghash.cpp
		i686-w64-mingw32-g++ -static-libgcc -shared bitmsghash.o \
                    -D_WIN32 -O3 -march=native \
                    "-I$HOME/.wine32/drive_c/OpenSSL-Win32/include" \
                    "-L$HOME/.wine32/drive_c/OpenSSL-Win32/lib/MinGW" \
                    -fPIC -shared -lcrypt32 -leay32 -lwsock32 \
                    -o bitmsghash32.dll -Wl,--out-implib,bitmsghash.a
	fi
}

function build_exe(){
	cd "${BASE_DIR}" || exit 1
	cd packages/pyinstaller || exit 1
	wine pyinstaller bitmessagemain.spec
}

# prepare on ubuntu
# dpkg --add-architecture i386
# apt update
# apt -y install wget wine-stable wine-development winetricks mingw-w64 wine32 wine64 xvfb


download_sources
if [ "$1" == "--download-only" ]; then
	exit
fi

install_wine
install_python
install_pyqt
install_openssl
install_pyopencl
install_msgpack
install_pyinstaller
build_dll
build_exe
