FROM ubuntu:jammy

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    software-properties-common build-essential libcap-dev libffi-dev \
    libssl-dev python-all-dev python-is-python3 python-setuptools \
    python3-dev python3-pip language-pack-en qt5dxcb-plugin tor xvfb

RUN pip install tox

ADD . .

CMD .buildbot/tox-jammy/test.sh
