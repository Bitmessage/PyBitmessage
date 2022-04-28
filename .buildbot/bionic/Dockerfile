FROM ubuntu:bionic AS test_bionic

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get install -yq --no-install-suggests --no-install-recommends \
    buildbot-slave git subversion python3-dev libffi-dev python3-setuptools \
    python3-pip dumb-init curl openssh-client wget \
    python-qt4 python-pyqt5 \
    build-essential libcap-dev libmtdev-dev xvfb tor xclip python3-opencv

RUN pip3 install coverage psutil pycrypto \
    xvfbwrapper python_prctl six
