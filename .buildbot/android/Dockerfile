# A container for buildbot

FROM ubuntu:focal AS android

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME="/opt/android"

RUN apt-get update -qq > /dev/null \
    && apt-get -y install -qq --no-install-recommends locales \
    && locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system/build dependencies
RUN apt-get -y update -qq \
    && apt-get -y install -qq --no-install-recommends \
    curl autoconf automake build-essential cmake git nano libtool \
    libltdl-dev libffi-dev libssl-dev \
    patch pkg-config python-is-python3 python3-dev python3-pip unzip zip

RUN apt-get -y install -qq --no-install-recommends openjdk-17-jdk \
    && apt-get -y autoremove

# pyzbar dependencies
RUN apt-get -y install -qq --no-install-recommends libzbar0 libtool gettext

RUN pip install buildozer cython virtualenv


ENV ANDROID_NDK_HOME="${ANDROID_HOME}/android-ndk"
ENV ANDROID_NDK_VERSION="25b"
ENV ANDROID_NDK_HOME_V="${ANDROID_NDK_HOME}-r${ANDROID_NDK_VERSION}"

# get the latest version from https://developer.android.com/ndk/downloads/index.html
ENV ANDROID_NDK_ARCHIVE="android-ndk-r${ANDROID_NDK_VERSION}-linux.zip"
ENV ANDROID_NDK_DL_URL="https://dl.google.com/android/repository/${ANDROID_NDK_ARCHIVE}"
# download and install Android NDK
RUN curl "${ANDROID_NDK_DL_URL}" --output "${ANDROID_NDK_ARCHIVE}" \
    && mkdir -p "${ANDROID_NDK_HOME_V}" \
    && unzip -q "${ANDROID_NDK_ARCHIVE}" -d "${ANDROID_HOME}" \
    && ln -sfn "${ANDROID_NDK_HOME_V}" "${ANDROID_NDK_HOME}" \
    && rm -rf "${ANDROID_NDK_ARCHIVE}"

ENV ANDROID_SDK_HOME="${ANDROID_HOME}/android-sdk"

# get the latest version from https://developer.android.com/studio/index.html
ENV ANDROID_SDK_TOOLS_VERSION="11076708"
ENV ANDROID_SDK_BUILD_TOOLS_VERSION="34.0.0"
ENV ANDROID_SDK_CMDLINE_TOOLS_VERSION="12.0"
ENV ANDROID_SDK_TOOLS_ARCHIVE="commandlinetools-linux-${ANDROID_SDK_TOOLS_VERSION}_latest.zip"
ENV ANDROID_SDK_TOOLS_DL_URL="https://dl.google.com/android/repository/${ANDROID_SDK_TOOLS_ARCHIVE}"
ENV ANDROID_CMDLINE_TOOLS_DIR="${ANDROID_SDK_HOME}/cmdline-tools/${ANDROID_SDK_CMDLINE_TOOLS_VERSION}"
ENV ANDROID_SDK_MANAGER="${ANDROID_CMDLINE_TOOLS_DIR}/bin/sdkmanager --sdk_root=${ANDROID_SDK_HOME}"

# download and install Android SDK
RUN curl "${ANDROID_SDK_TOOLS_DL_URL}" --output "${ANDROID_SDK_TOOLS_ARCHIVE}" \
    && mkdir -p "${ANDROID_SDK_HOME}/cmdline-tools" \
    && unzip -q "${ANDROID_SDK_TOOLS_ARCHIVE}" \
       -d "${ANDROID_SDK_HOME}/cmdline-tools" \
    && mv "${ANDROID_SDK_HOME}/cmdline-tools/cmdline-tools" \
       ${ANDROID_CMDLINE_TOOLS_DIR} \
    && ln -sfn ${ANDROID_CMDLINE_TOOLS_DIR} "${ANDROID_SDK_HOME}/tools" \
    && rm -rf "${ANDROID_SDK_TOOLS_ARCHIVE}"

# update Android SDK, install Android API, Build Tools...
RUN mkdir -p "${ANDROID_SDK_HOME}/.android/" \
    && echo '### User Sources for Android SDK Manager' \
        > "${ANDROID_SDK_HOME}/.android/repositories.cfg"

# accept Android licenses (JDK necessary!)
RUN yes | ${ANDROID_SDK_MANAGER} --licenses > /dev/null

# download platforms, API, build tools
RUN ${ANDROID_SDK_MANAGER} "platforms;android-30" > /dev/null \
    && ${ANDROID_SDK_MANAGER} "platforms;android-28" > /dev/null \
    && ${ANDROID_SDK_MANAGER} "platform-tools" > /dev/null \
    && ${ANDROID_SDK_MANAGER} "build-tools;${ANDROID_SDK_BUILD_TOOLS_VERSION}" \
    > /dev/null \
    && ${ANDROID_SDK_MANAGER} "extras;android;m2repository" > /dev/null \
    && chmod +x "${ANDROID_CMDLINE_TOOLS_DIR}/bin/avdmanager"

# download ANT
ENV APACHE_ANT_VERSION="1.9.4"
ENV APACHE_ANT_ARCHIVE="apache-ant-${APACHE_ANT_VERSION}-bin.tar.gz"
ENV APACHE_ANT_DL_URL="https://archive.apache.org/dist/ant/binaries/${APACHE_ANT_ARCHIVE}"
ENV APACHE_ANT_HOME="${ANDROID_HOME}/apache-ant"
ENV APACHE_ANT_HOME_V="${APACHE_ANT_HOME}-${APACHE_ANT_VERSION}"

RUN curl "${APACHE_ANT_DL_URL}" --output "${APACHE_ANT_ARCHIVE}" \
    && tar -xf "${APACHE_ANT_ARCHIVE}" -C "${ANDROID_HOME}" \
    && ln -sfn "${APACHE_ANT_HOME_V}" "${APACHE_ANT_HOME}" \
    && rm -rf "${APACHE_ANT_ARCHIVE}"


RUN useradd -m -U builder && mkdir /android

WORKDIR /android

RUN chown -R builder.builder /android "${ANDROID_SDK_HOME}" \
    && chmod -R go+w "${ANDROID_SDK_HOME}"

USER builder

ADD . .
