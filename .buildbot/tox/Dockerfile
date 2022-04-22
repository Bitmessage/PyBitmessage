FROM ubuntu:bionic AS tox

RUN apt-get update

# Common apt packages
RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    software-properties-common build-essential libcap-dev libssl-dev \
    python-all-dev python-setuptools wget xvfb language-pack-en \
    libffi-dev python3-dev python3-pip python3.8 python3.8-dev python3.8-venv \
    python-msgpack python-pip python-qt4 python-six qtbase5-dev qt5-default \
    tor

RUN python3.8 -m pip install setuptools wheel
RUN python3.8 -m pip install --upgrade pip tox virtualenv

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
