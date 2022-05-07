FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    software-properties-common build-essential libcap-dev libffi-dev \
    libssl-dev python-all-dev python-setuptools \
    python3-dev python3-pip python3.9 python3.9-dev python3.9-venv \
    language-pack-en qt5dxcb-plugin tor xvfb

RUN python3.9 -m pip install --upgrade pip tox virtualenv
