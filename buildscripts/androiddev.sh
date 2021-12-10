#!/bin/sh
# This is a comment!
echo Hello android       # This is a comment, too!

ANDROID_HOME="/opt/android"
get_python_version=3
echo "#################################################################################"
echo $get_python_version
echo "#################################################################################"


# SYSTEM DEPENDENCIES
system_dependencies ()
{   
    echo "installing system dependencies......................."
    echo $(python -V)
    echo $get_python_version

    apt -y update -qq
    apt -y install --no-install-recommends python3-pip pip3 python3 virtualenv python3-setuptools python3-wheel git wget unzip sudo patch bzip2 lzma
    apt -y autoremove

}    

build_dependencies ()
{   
    echo "installing build dependencies..............."
    dpkg --add-architecture i386
    apt -y update -qq    
    apt -y install -qq --no-install-recommends build-essential ccache git python3 python3-dev libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 zip zlib1g-dev zlib1g:i386
    apt -y autoremove
    apt -y clean
}

specific_recipes_dependencies ()
{   
    echo "installing dependent recipes................."
    dpkg --add-architecture i386
    apt -y update -qq
    apt -y install -qq --no-install-recommends libffi-dev autoconf automake cmake gettext libltdl-dev libtool pkg-config
    apt -y autoremove
    apt -y clean
}

install_android_pkg ()
{
    echo "installing android packages................"
    BUILDOZER_VERSION=1.2.0
    CYTHON_VERSION=0.29.15
    pip3 install buildozer==$BUILDOZER_VERSION 
    pip3 install --upgrade cython==$CYTHON_VERSION
}

install_ndk()
{   
    echo "installing ndk............................."
    ANDROID_NDK_VERSION=23b
    ANDROID_NDK_HOME="${ANDROID_HOME}/android-ndk"                                                  
    ANDROID_NDK_HOME_V="${ANDROID_NDK_HOME}-r${ANDROID_NDK_VERSION}"
    # get the latest version from https://developer.android.com/ndk/downloads/index.html
    ANDROID_NDK_ARCHIVE="android-ndk-r${ANDROID_NDK_VERSION}-linux.zip"
    ANDROID_NDK_DL_URL="https://dl.google.com/android/repository/${ANDROID_NDK_ARCHIVE}"
    echo $ANDROID_NDK_DL_URL
    echo "Downloading ndk.........................................................................."
    wget -nc ${ANDROID_NDK_DL_URL}
    mkdir --parents "${ANDROID_NDK_HOME_V}"     
    unzip -q "${ANDROID_NDK_ARCHIVE}" -d "${ANDROID_HOME}" 
    ln -sfn "${ANDROID_NDK_HOME_V}" "${ANDROID_NDK_HOME}" 
    rm -rf "${ANDROID_NDK_ARCHIVE}"
}

system_dependencies
build_dependencies
specific_recipes_dependencies
install_android_pkg
install_ndk