# A container for buildbot
FROM ubuntu:focal AS transifex

ENV DEBIAN_FRONTEND=noninteractive

ENV SKIPCACHE=2022-12-14

RUN apt-get update

RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    software-properties-common build-essential libcap-dev libssl-dev \
    python3-dev python3-pip python3-virtualenv libmtdev-dev libpq-dev \
    python-all-dev python-setuptools wget xvfb

# RUN wget -O /usr/local/bin/pybitmesage.wsgi https://git.bitmessage.org/Bitmessage/buildbot-scripts/raw/branch/master/pybitmesage.wsgi
# RUN chmod +x /usr/local/bin/pybitmesage.wsgi
