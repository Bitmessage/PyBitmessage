#!/bin/bash

# INIT
MACHINE_TYPE=`uname -m`
BASE_DIR=$(pwd)
PYTHON_VERSION=2.7.15
PYQT_VERSION=4-4.11.4-gpl-Py2.7-Qt4.8.7
OPENSSL_VERSION=1_0_2s
DIRECTORY32BIT=SoftwareDownloads32bit
DIRECTORY64BIT=SoftwareDownloads64bit

if [ ${MACHINE_TYPE} == 'x86_64' ]; then
	if [ ! -d "$DIRECTORY64BIT" ]; then
		mkdir SoftwareDownloads64bit
        cd SoftwareDownloads64bit
    else
    	echo "Directory already exists"
    	cd SoftwareDownloads64bit
	fi
else
	if [ ! -d "$DIRECTORY32BIT" ]; then
		mkdir SoftwareDownloads32bit
        cd SoftwareDownloads32bit
    else
    	echo "Directory 32 bit alrready exists"
    	cd SoftwareDownloads32bit
	fi
fi
#Functions
function install_wine {

	
	wget -nc https://dl.winehq.org/wine-builds/Release.key  --no-check-certificate
	sudo apt-key add Release.key
	sudo apt-add-repository 'https://dl.winehq.org/wine-builds/ubuntu/'
	sudo apt-get -y update
	sudo apt-get install wine1.8
	sudo apt-get install wine1.8 winetricks
	if [ ${MACHINE_TYPE} == 'x86_64' ]; then
		sudo apt-get install wine64-development
		env WINEPREFIX=$HOME/.wine64 WINEARCH=win64 winecfg
		WINE="env WINEPREFIX=$HOME/.wine64 wine"
		export WINEPREFIX
		
	else
		sudo apt-get install wine32-development
		env WINEPREFIX=$HOME/.wine32 WINEARCH=win32 winecfg
		WINE="env WINEPREFIX=$HOME/.wine32 wine"
		export WINEPREFIX
		
	fi
}

function install_python(){
	echo "Download Python2.7"
	
	if [ ${MACHINE_TYPE} == 'x86_64' ]; then
		# For 64 bit machine
		wget -nc wget http://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}.amd64.msi --no-check-certificate
		echo "Install Python2.7 for 64 bit"
  		$WINE msiexec -i python-${PYTHON_VERSION}.amd64.msi /qn
		
		wget -nc https://download.microsoft.com/download/d/2/4/d242c3fb-da5a-4542-ad66-f9661d0a8d19/vcredist_x64.exe --no-check-certificate
		$WINE vcredist_x64.exe		
		echo "Installed vcredist for 64 bit"
		$WINE pip install --upgrade pip

	else
		# For 32 bit machine
		cd SoftwareDownloads32bit
		wget -nc https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}.msi --no-check-certificate
		echo "Install Python2.7 for 32 bit"
  		$WINE msiexec -i python-${PYTHON_VERSION}.msi /qn

  		echo "Installing vc_redist for 32 bit " 		
		wget -nc https://download.microsoft.com/download/1/1/1/1116b75a-9ec3-481a-a3c8-1777b5381140/vcredist_x86.exe --no-check-certificate
  		$WINE vcredist_x86.exe
  		
  		#insatlled msvcr120.dll for 32 bit system 
  		wget -nc http://www.dll-found.com/zip/m/msvcr120.dll.zip --no-check-certificate
		unzip msvcr120.dll.zip
		sudo cp msvcr120.dll $HOME/.wine32/drive_c/windows/system32/
		$WINE pip install --upgrade pip

	fi
}

function install_pyqt(){
	
	echo "Download PyQT"
	if [ ${MACHINE_TYPE} == 'x86_64' ]; then
		# For 64 bit machine
		rm -rf PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x64.exe
		rm -rf Cross_Compilation
  		git clone  https://github.com/surbhicis/Cross_Compilation
  		$WINE Cross_Compilation/PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x64.exe /silent /verysiling /sp- /suppressmsgboxes
	else
		# For 32 bit machine
		cd SoftwareDownloads32bit
  		wget -nc https://github.com/dhb52/python-lib/raw/master/PyQt4-4.11.4-cp27-cp27m-win32.whl --no-check-certificate
  		echo "Install PyQt4-4 for 32 bit"
  		$WINE pip install PyQt4-4.11.4-cp27-cp27m-win32.whl
	fi
}

function install_openssl(){
	if [ ${MACHINE_TYPE} == 'x86_64' ]; then
		wget -nc https://slproweb.com/download/Win64OpenSSL-1_0_2s.exe --no-check-certificate
	  	$WINE Win64OpenSSL-1_0_2s.exe  /silent /verysiling /sp- /suppressmsgboxes

	else
		cd SoftwareDownloads32bit
		wget -nc https://slproweb.com/download/Win32OpenSSL-${OPENSSL_VERSION}.exe --no-check-certificate
	  	$WINE Win32OpenSSL-${OPENSSL_VERSION}.exe  /silent /verysiling /sp- /suppressmsgboxes
	  	echo "Install PyInstaller 32 bit"
	fi
}

function install_pyinstaller()
{
	$WINE pip install pyinstaller
	echo "Install PyInstaller"	
	echo "Install Pyopencl"
	
	if [ ${MACHINE_TYPE} == 'x86_64' ]; then
		wget -nc https://www.silx.org/pub/wheelhouse/old/pyopencl-2015.1-cp27-none-win_amd64.whl --no-check-certificate
		$WINE pip install pyopencl-2015.1-cp27-none-win_amd64.whl
		$WINE pip install msgpack-python
		
	else
		wget -nc https://download.bitmessage.org/whl/pyopencl-2015.1-cp27-none-win32.whl --no-check-certificate
		$WINE pip install msgpack-python
		$WINE pip install pyopencl-2015.1-cp27-none-win32.whl
	fi
	echo "Install Message Pack"
	
}


function build_dll(){
	cd $BASE_DIR
	# rm -rf master.zip
	# rm -rf PyBitmessage
	# git clone https://github.com/Bitmessage/PyBitmessage.git
	echo "Current directory"
	echo `pwd`
	cd PyBitmessage/src/bitmsghash
	if [ ${MACHINE_TYPE} == 'x86_64' ]; then
		# Do stuff for 64 bit machine
		echo "Install MinGW"
		sudo apt-get install mingw-w64
		echo "Create dll"
		x86_64-w64-mingw32-g++ -D_WIN32 -Wall -O3 -march=native -I/home/cis/.wine64/drive_c/OpenSSL-Win64/include -I/usr/x86_64-w64-mingw32/include -L/home/cis/.wine64/drive_c/OpenSSL-Win64/lib -c 	bitmsghash.cpp
		x86_64-w64-mingw32-g++ -static-libgcc -shared bitmsghash.o -D_WIN32 -O3 -march=native  -I/home/cis/.wine64/drive_c/OpenSSL-Win64/include -L/home/cis/.wine64/drive_c/OpenSSL-Win64 -L/usr/lib/x86_64-linux-gnu/wine -fPIC -shared -lcrypt32 -leay32 -lwsock32 -o bitmsghash64.dll -Wl,--out-implib,bitmsghash.a
		echo "DLL generated successfully "
		cd ../..

		env WINEPREFIX=$HOME/.wine64 wine pyinstaller packages/pyinstaller/bitmessagemain.spec
	else
		echo "Install MinGW for 32 bit"
		sudo apt-get install mingw-w64
		echo "Create dll"
		
		
		i686-w64-mingw32-g++ -D_WIN32 -Wall -m32 -O3 -march=native   -I$HOME/.wine32/drive_c/OpenSSL-Win32/include -I/usr/i686-w64-mingw32/include  -L$HOME/.wine32/drive_c/OpenSSL-Win32/lib  -c 	bitmsghash.cpp
		i686-w64-mingw32-g++ -static-libgcc -shared bitmsghash.o -D_WIN32 -O3 -march=native    -I$HOME/.wine32/drive_c/OpenSSL-Win32/include    -L$HOME/.wine32/drive_c/OpenSSL-Win32/lib/MinGW -fPIC -shared -lcrypt32 -leay32 -lwsock32  -o bitmsghash32.dll  -Wl,--out-implib,bitmsghash.a 
		cd ../..

		env WINEPREFIX=$HOME/.wine32 wine pyinstaller packages/pyinstaller/bitmessagemain.spec
	fi		
}


# install_wine
# install_python
# install_pyqt
# install_openssl
# install_pyinstaller
build_dll
