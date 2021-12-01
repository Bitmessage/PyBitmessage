#!/bin/bash

ANDROID_HOME="/opt/android"
get_python_version=$@ 

#INSTALL ANDROID PACKAGES 
function install_android_pkg ()
{
    if [[ "$get_python_version" -eq " 2 " ]];
    then
        BUILDOZER_VERSION=0.39
        CYTHON_VERSION=0.28.6
    elif [[ "$get_python_version" -eq " 3 " ]];
    then    
        BUILDOZER_VERSION=1.0
        CYTHON_VERSION=0.29.15
    else
        exit    
    fi
    pip3 install buildozer==$BUILDOZER_VERSION 
    pip3 install --upgrade cython==$CYTHON_VERSION
}

# SYSTEM DEPENDENCIES
function system_dependencies ()
{
    if [[ "$get_python_version" -eq " 2 " ]];
    then
        apt -y update -qq
        apt -y install -qq --no-install-recommends python virtualenv python-pip python-setuptools python-wheel git wget unzip lbzip2 patch sudo software-properties-common

    elif [[ "$get_python_version" -eq " 3 " ]];
    then
        apt -y update -qq   
        apt -y install --no-install-recommends python3-pip pip3 python3 virtualenv python3-setuptools python3-wheel git wget unzip sudo patch bzip2 lzma
    else
        exit    
    fi  
    apt -y autoremove
}

# build dependencies
# https://buildozer.readthedocs.io/en/latest/installation.html#android-on-ubuntu-16-04-64bit
function build_dependencies ()
{
    dpkg --add-architecture i386
    apt -y update -qq
    if [[ "$get_python_version" -eq " 2 " ]];
    then
        apt -y install -qq --no-install-recommends build-essential ccache git python python-dev libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 zip zlib1g-dev zlib1g:i386
    elif [[ "$get_python_version" -eq " 3 " ]];
    then    
        apt -y install -qq --no-install-recommends build-essential ccache git python3 python3-dev libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 zip zlib1g-dev zlib1g:i386
    else
        exit
    fi
    apt -y autoremove
    apt -y clean
}    

# RECIPES DEPENDENCIES
function specific_recipes_dependencies ()
{
    apt -y update -qq
    apt -y install -qq --no-install-recommends libffi-dev autoconf automake cmake gettext libltdl-dev libtool pkg-config
    apt -y autoremove
    apt -y clean
}

# INSTALL NDK
function install_ndk()
{   
    if [[ "$get_python_version" -eq " 2 " ]];
    then
        ANDROID_NDK_VERSION="17c"
    elif [[ "$get_python_version" -eq " 3 " ]];
    then    
        ANDROID_NDK_VERSION=21
    else
        # echo "-----"
        exit    
    fi
    ANDROID_NDK_HOME="${ANDROID_HOME}/android-ndk"
    ANDROID_NDK_HOME_V="${ANDROID_NDK_HOME}-r${ANDROID_NDK_VERSION}"
    # get the latest version from https://developer.android.com/ndk/downloads/index.html
    ANDROID_NDK_ARCHIVE="android-ndk-r${ANDROID_NDK_VERSION}-linux-x86_64.zip"
    ANDROID_NDK_DL_URL="https://dl.google.com/android/repository/${ANDROID_NDK_ARCHIVE}"
    echo "Downloading ndk.........................................................................."
    wget -nc ${ANDROID_NDK_DL_URL}
    mkdir --parents "${ANDROID_NDK_HOME_V}"     
    unzip -q "${ANDROID_NDK_ARCHIVE}" -d "${ANDROID_HOME}" 
    ln -sfn "${ANDROID_NDK_HOME_V}" "${ANDROID_NDK_HOME}" 
    rm -rf "${ANDROID_NDK_ARCHIVE}"
}

# INSTALL SDK
function install_sdk()
{
    if [[ "$get_python_version" -eq " 2 " ]];
    then
        ANDROID_SDK_BUILD_TOOLS_VERSION="28.0.3"
    elif [[ "$get_python_version" -eq " 3 " ]];
    then    
        ANDROID_SDK_BUILD_TOOLS_VERSION="29.0.2"
    else
        exit    
    fi       
    ANDROID_SDK_HOME="${ANDROID_HOME}/android-sdk"
    # get the latest version from https://developer.android.com/studio/index.html
    ANDROID_SDK_TOOLS_VERSION="4333796"
    ANDROID_SDK_TOOLS_ARCHIVE="sdk-tools-linux-${ANDROID_SDK_TOOLS_VERSION}.zip"
    ANDROID_SDK_TOOLS_DL_URL="https://dl.google.com/android/repository/${ANDROID_SDK_TOOLS_ARCHIVE}"
    echo "Downloading sdk.........................................................................."
    wget -nc ${ANDROID_SDK_TOOLS_DL_URL}
    mkdir --parents "${ANDROID_SDK_HOME}"
    unzip -q "${ANDROID_SDK_TOOLS_ARCHIVE}" -d "${ANDROID_SDK_HOME}"
    rm -rf "${ANDROID_SDK_TOOLS_ARCHIVE}"
     # update Android SDK, install Android API, Build Tools...
    mkdir --parents "${ANDROID_SDK_HOME}/.android/" 
    echo '### Sources for Android SDK Manager' > "${ANDROID_SDK_HOME}/.android/repositories.cfg"
    # accept Android licenses (JDK necessary!)
    apt -y update -qq
    apt -y install -qq --no-install-recommends openjdk-8-jdk
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
function install_ant()
{
    if [[ "$get_python_version" -eq " 2 " ]];
    then
        APACHE_ANT_VERSION="1.9.4"
    elif [[ "$get_python_version" -eq " 3 " ]];
    then    
        APACHE_ANT_VERSION="1.10.7"
    else
        exit    
    fi   

    APACHE_ANT_ARCHIVE="apache-ant-${APACHE_ANT_VERSION}-bin.tar.gz"
    APACHE_ANT_DL_URL="http://archive.apache.org/dist/ant/binaries/${APACHE_ANT_ARCHIVE}"
    APACHE_ANT_HOME="${ANDROID_HOME}/apache-ant"
    APACHE_ANT_HOME_V="${APACHE_ANT_HOME}-${APACHE_ANT_VERSION}"
    echo "Downloading ant.........................................................................."
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