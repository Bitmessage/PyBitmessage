# A container for buildbot
FROM ubuntu:bionic AS android
# FROM ubuntu:20.04 AS buildbot-bionic

RUN apt -y update -qq
RUN apt -y install wget

RUN wget -nc "https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip"
RUN wget -nc "https://dl.google.com/android/repository/android-ndk-r23b-linux.zip"
RUN wget -nc "http://archive.apache.org/dist/ant/binaries/apache-ant-1.10.12-bin.tar.gz"

# SYSTEM DEPENDENCIES

RUN apt -y install --no-install-recommends python3-pip \
    pip3 python3 virtualenv python3-setuptools \
    python3-wheel git unzip sudo patch bzip2 lzma
RUN apt -y autoremove

# BUILD DEPENDENCIES

RUN dpkg --add-architecture i386
RUN apt -y update -qq    
RUN apt -y install -qq --no-install-recommends build-essential \
    ccache git python3 python3-dev libncurses5:i386 libstdc++6:i386 \
    libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 \
    libidn11:i386 zip zlib1g-dev zlib1g:i386
RUN apt -y autoremove
RUN apt -y clean

# RECIPES DEPENDENCIES

RUN dpkg --add-architecture i386
RUN apt -y update -qq
RUN apt -y install -qq --no-install-recommends libffi-dev autoconf \
    automake cmake gettext libltdl-dev libtool pkg-config
RUN apt -y autoremove
RUN apt -y clean

# INSTALL ANDROID PACKAGES

RUN pip3 install buildozer==1.2.0 
RUN pip3 install --upgrade cython==0.29.15

# INSTALL NDK

# get the latest version from https://developer.android.com/ndk/downloads/index.html
RUN mkdir --parents "/opt/android/android-ndk-r23b"
RUN unzip -q "android-ndk-r23b-linux.zip" -d "/opt/android"
RUN ln -sfn "/opt/android/android-ndk-r23b" "/opt/android/android-ndk"
RUN rm -rf "android-ndk-r23b-linux.zip"

# INSTALL APACHE-ANT

RUN tar -xf "apache-ant-1.10.12-bin.tar.gz" -C "/opt/android"
RUN ln -sfn "/opt/android/apache-ant-1.10.12" "/opt/android/apache-ant"
RUN rm -rf "apache-ant-1.10.12-bin.tar.gz"

# INSTALL SDK

# get the latest version from https://developer.android.com/studio/index.html
RUN mkdir --parents "/opt/android/android-sdk"
RUN unzip -q "sdk-tools-linux-4333796.zip" -d "/opt/android/android-sdk"
RUN rm -rf "sdk-tools-linux-4333796.zip"
 # update Android SDK, install Android API, Build Tools...
RUN mkdir --parents "/opt/android/android-sdk/.android/" 
# accept Android licenses (JDK necessary!)
RUN apt -y update -qq
RUN apt -y install -qq --no-install-recommends openjdk-11-jdk
RUN apt -y autoremove
RUN yes | "/opt/android/android-sdk/tools/bin/sdkmanager" "build-tools;29.0.2" > /dev/null    
# download platforms, API, build tools
RUN "/opt/android/android-sdk/tools/bin/sdkmanager" "platforms;android-24" > /dev/null
RUN "/opt/android/android-sdk/tools/bin/sdkmanager" "platforms;android-28" > /dev/null
RUN "/opt/android/android-sdk/tools/bin/sdkmanager" "build-tools;29.0.2" > /dev/null
RUN "/opt/android/android-sdk/tools/bin/sdkmanager" "extras;android;m2repository" > /dev/null
RUN find /opt/android/android-sdk -type f -perm /0111 -print0|xargs -0 chmod a+x
RUN chown -R buildbot.buildbot /opt/android/android-sdk
RUN chmod +x "/opt/android/android-sdk/tools/bin/avdmanager" 
