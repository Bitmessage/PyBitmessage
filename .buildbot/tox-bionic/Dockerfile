FROM ubuntu:bionic

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    software-properties-common build-essential libcap-dev libffi-dev \
    libssl-dev python-all-dev python-setuptools \
    python3-dev python3-pip python3.8 python3.8-dev python3.8-venv \
    python-msgpack python-qt4 language-pack-en qt5dxcb-plugin tor xvfb

RUN apt-get install -yq sudo

RUN echo 'builder ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN python3.8 -m pip install setuptools wheel
RUN python3.8 -m pip install --upgrade pip tox virtualenv

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
