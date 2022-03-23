# A container for PyBitmessage daemon

FROM ubuntu:bionic

RUN apt-get update

# Install dependencies
RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    build-essential libcap-dev libssl-dev \
    python-all-dev python-msgpack python-pip python-setuptools

EXPOSE 8444 8442

ENV HOME /home/bitmessage
ENV BITMESSAGE_HOME ${HOME}

WORKDIR ${HOME}
ADD . ${HOME}
COPY packages/docker/launcher.sh /usr/bin/

# Install
RUN pip2 install jsonrpclib .

# Cleanup
RUN rm -rf /var/lib/apt/lists/*
RUN rm -rf ${HOME}

# Create a user
RUN useradd -r bitmessage && chown -R bitmessage ${HOME}

USER bitmessage

# Generate default config
RUN pybitmessage -t

ENTRYPOINT ["launcher.sh"]
CMD ["-d"]
