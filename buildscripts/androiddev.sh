#!/bin/sh

ANDROID_HOME="/opt/android"
get_python_version=3

# INSTALL ANDROID PACKAGES 
install_android_pkg ()
{
    BUILDOZER_VERSION=1.2.0
    CYTHON_VERSION=0.29.15
    pip3 install buildozer==$BUILDOZER_VERSION 
    pip3 install --upgrade cython==$CYTHON_VERSION
}

# SYSTEM DEPENDENCIES
system_dependencies ()
{
    apt -y update -qq
    apt -y install --no-install-recommends python3-pip pip3 python3 virtualenv python3-setuptools python3-wheel git wget unzip sudo patch bzip2 lzma
    apt -y autoremove
}

# build dependencies
# https://buildozer.readthedocs.io/en/latest/installation.html#android-on-ubuntu-16-04-64bit
build_dependencies ()
{
    dpkg --add-architecture i386
    apt -y update -qq    
    apt -y install -qq --no-install-recommends build-essential ccache git python3 python3-dev libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 zip zlib1g-dev zlib1g:i386
    apt -y autoremove
    apt -y clean
}    

# RECIPES DEPENDENCIES
specific_recipes_dependencies ()
{
    dpkg --add-architecture i386
    apt -y update -qq
    apt -y install -qq --no-install-recommends libffi-dev autoconf automake cmake gettext libltdl-dev libtool pkg-config
    apt -y autoremove
    apt -y clean
}

# INSTALL NDK
install_ndk()
{
    ANDROID_NDK_VERSION=23b
    ANDROID_NDK_HOME="${ANDROID_HOME}/android-ndk"
    ANDROID_NDK_HOME_V="${ANDROID_NDK_HOME}-r${ANDROID_NDK_VERSION}"
    # get the latest version from https://developer.android.com/ndk/downloads/index.html
    ANDROID_NDK_ARCHIVE="android-ndk-r${ANDROID_NDK_VERSION}-linux.zip"
    ANDROID_NDK_DL_URL="https://dl.google.com/android/repository/${ANDROID_NDK_ARCHIVE}"
    wget -nc ${ANDROID_NDK_DL_URL}
    mkdir --parents "${ANDROID_NDK_HOME_V}"
    unzip -q "${ANDROID_NDK_ARCHIVE}" -d "${ANDROID_HOME}"
    ln -sfn "${ANDROID_NDK_HOME_V}" "${ANDROID_NDK_HOME}"
    rm -rf "${ANDROID_NDK_ARCHIVE}"
}

# INSTALL SDK
install_sdk()
{
    ANDROID_SDK_BUILD_TOOLS_VERSION="29.0.2"     
    ANDROID_SDK_HOME="${ANDROID_HOME}/android-sdk"
    # get the latest version from https://developer.android.com/studio/index.html
    ANDROID_SDK_TOOLS_VERSION="4333796"
    ANDROID_SDK_TOOLS_ARCHIVE="sdk-tools-linux-${ANDROID_SDK_TOOLS_VERSION}.zip"
    ANDROID_SDK_TOOLS_DL_URL="https://dl.google.com/android/repository/${ANDROID_SDK_TOOLS_ARCHIVE}"
    wget -nc ${ANDROID_SDK_TOOLS_DL_URL}
    mkdir --parents "${ANDROID_SDK_HOME}"
    unzip -q "${ANDROID_SDK_TOOLS_ARCHIVE}" -d "${ANDROID_SDK_HOME}"
    rm -rf "${ANDROID_SDK_TOOLS_ARCHIVE}"
     # update Android SDK, install Android API, Build Tools...
    mkdir --parents "${ANDROID_SDK_HOME}/.android/" 
    echo '### Sources for Android SDK Manager' > "${ANDROID_SDK_HOME}/.android/repositories.cfg"
    # accept Android licenses (JDK necessary!)
    apt -y update -qq
    apt -y install -qq --no-install-recommends openjdk-11-jdk
    apt -y autoremove
    yes | "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "build-tools;${ANDROID_SDK_BUILD_TOOLS_VERSION}" > /dev/null    
    # download platforms, API, build tools
    "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "platforms;android-24" > /dev/null
    "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "platforms;android-28" > /dev/null
    "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "build-tools;${ANDROID_SDK_BUILD_TOOLS_VERSION}" > /dev/null
    "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "extras;android;m2repository" > /dev/null
    find /opt/android/android-sdk -type f -perm /0111 -print0|xargs -0 chmod a+x
    chown -R buildbot.buildbot /opt/android/android-sdk
    chmod +x "${ANDROID_SDK_HOME}/tools/bin/avdmanager" 
}

# INSTALL APACHE-ANT
install_ant()
{
    APACHE_ANT_VERSION="1.10.12"   

    APACHE_ANT_ARCHIVE="apache-ant-${APACHE_ANT_VERSION}-bin.tar.gz"
    APACHE_ANT_DL_URL="http://archive.apache.org/dist/ant/binaries/${APACHE_ANT_ARCHIVE}"
    APACHE_ANT_HOME="${ANDROID_HOME}/apache-ant"
    APACHE_ANT_HOME_V="${APACHE_ANT_HOME}-${APACHE_ANT_VERSION}"
    wget -nc ${APACHE_ANT_DL_URL}
    tar -xf "${APACHE_ANT_ARCHIVE}" -C "${ANDROID_HOME}"
    ln -sfn "${APACHE_ANT_HOME_V}" "${APACHE_ANT_HOME}"
    rm -rf "${APACHE_ANT_ARCHIVE}"    
}

system_dependencies
build_dependencies
specific_recipes_dependencies
install_android_pkg
install_ndk
install_sdk
install_ant