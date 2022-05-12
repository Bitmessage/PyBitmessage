
# A container for buildbot
FROM ubuntu:bionic AS android
# FROM ubuntu:20.04 AS buildbot-bionic

ENV ANDROID_HOME="/opt/android"

RUN apt -y update -qq \
    && apt -y install -qq --no-install-recommends curl unzip ca-certificates \
    && apt -y autoremove


ENV ANDROID_NDK_HOME="${ANDROID_HOME}/android-ndk"
ENV ANDROID_NDK_VERSION="22b"
ENV ANDROID_NDK_HOME_V="${ANDROID_NDK_HOME}-r${ANDROID_NDK_VERSION}"

# get the latest version from https://developer.android.com/ndk/downloads/index.html
ENV ANDROID_NDK_ARCHIVE="android-ndk-r${ANDROID_NDK_VERSION}-linux-x86_64.zip"
ENV ANDROID_NDK_DL_URL="https://dl.google.com/android/repository/${ANDROID_NDK_ARCHIVE}"

# download and install Android NDK
RUN curl "${ANDROID_NDK_DL_URL}" \
        --output "${ANDROID_NDK_ARCHIVE}" \
    && mkdir --parents "${ANDROID_NDK_HOME_V}" \
    && unzip -q "${ANDROID_NDK_ARCHIVE}" -d "${ANDROID_HOME}" \
    && ln -sfn "${ANDROID_NDK_HOME_V}" "${ANDROID_NDK_HOME}" \
    && rm -rf "${ANDROID_NDK_ARCHIVE}"

ENV ANDROID_SDK_HOME="${ANDROID_HOME}/android-sdk"

# get the latest version from https://developer.android.com/studio/index.html
ENV ANDROID_SDK_TOOLS_VERSION="8092744"
ENV ANDROID_SDK_BUILD_TOOLS_VERSION="30.0.3"
ENV ANDROID_SDK_TOOLS_ARCHIVE="commandlinetools-linux-${ANDROID_SDK_TOOLS_VERSION}_latest.zip"
ENV ANDROID_SDK_TOOLS_DL_URL="https://dl.google.com/android/repository/${ANDROID_SDK_TOOLS_ARCHIVE}"
ENV ANDROID_SDK_MANAGER="${ANDROID_SDK_HOME}/tools/bin/sdkmanager --sdk_root=${ANDROID_SDK_HOME}"

# download and install Android SDK
RUN curl "${ANDROID_SDK_TOOLS_DL_URL}" \
        --output "${ANDROID_SDK_TOOLS_ARCHIVE}" \
    && mkdir --parents "${ANDROID_SDK_HOME}" \
    && unzip -q "${ANDROID_SDK_TOOLS_ARCHIVE}" -d "${ANDROID_SDK_HOME}" \
    && mv "${ANDROID_SDK_HOME}/cmdline-tools" "${ANDROID_SDK_HOME}/tools" \
    && rm -rf "${ANDROID_SDK_TOOLS_ARCHIVE}"

# update Android SDK, install Android API, Build Tools...
RUN mkdir --parents "${ANDROID_SDK_HOME}/.android/" \
    && echo '### User Sources for Android SDK Manager' \
        > "${ANDROID_SDK_HOME}/.android/repositories.cfg"

# accept Android licenses (JDK necessary!)
RUN apt -y update -qq \
    && apt -y install -qq --no-install-recommends \
        openjdk-11-jdk-headless \
    && apt -y autoremove
RUN yes | ${ANDROID_SDK_MANAGER} --licenses > /dev/null

# download platforms, API, build tools
RUN ${ANDROID_SDK_MANAGER} "platforms;android-30" > /dev/null && \
    ${ANDROID_SDK_MANAGER} "build-tools;${ANDROID_SDK_BUILD_TOOLS_VERSION}" > /dev/null && \
    ${ANDROID_SDK_MANAGER} "extras;android;m2repository" > /dev/null && \
    chmod +x "${ANDROID_SDK_HOME}/tools/bin/avdmanager"

# download ANT
ENV APACHE_ANT_VERSION="1.9.4"
ENV APACHE_ANT_ARCHIVE="apache-ant-${APACHE_ANT_VERSION}-bin.tar.gz"
ENV APACHE_ANT_DL_URL="https://archive.apache.org/dist/ant/binaries/${APACHE_ANT_ARCHIVE}"
ENV APACHE_ANT_HOME="${ANDROID_HOME}/apache-ant"
ENV APACHE_ANT_HOME_V="${APACHE_ANT_HOME}-${APACHE_ANT_VERSION}"

RUN curl "${APACHE_ANT_DL_URL}" \
        --output "${APACHE_ANT_ARCHIVE}" \
    && tar -xf "${APACHE_ANT_ARCHIVE}" -C "${ANDROID_HOME}" \
    && ln -sfn "${APACHE_ANT_HOME_V}" "${APACHE_ANT_HOME}" \
    && rm -rf "${APACHE_ANT_ARCHIVE}"

# install system/build dependencies
RUN apt -y update -qq \
    && apt -y install -qq --no-install-recommends \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-venv \
        wget \
        lbzip2 \
        bzip2 \
        lzma \
        patch \
        sudo \
        software-properties-common \
        git \
        zip \
        unzip \
        build-essential \
        ccache \
        autoconf \
        libtool \
        pkg-config \
        zlib1g-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libtinfo5 \
        cmake \
        libffi-dev \
        libssl-dev \
        automake \
        gettext \
        libltdl-dev \
        libidn11 \
    && apt -y autoremove \
    && apt -y clean

# INSTALL ANDROID PACKAGES

RUN pip3 install buildozer==1.2.0 
RUN pip3 install --upgrade cython==0.29.15