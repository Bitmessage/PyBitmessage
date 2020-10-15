# A container for PyBitmessage daemon

FROM ubuntu:xenial

RUN apt-get update

# Install dependencies
RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    build-essential libcap-dev libssl-dev \
    python-all-dev python-msgpack python-pip python-setuptools

RUN pip2 install --upgrade pip

EXPOSE 8444 8442

ENV HOME /home/bitmessage
ENV BITMESSAGE_HOME ${HOME}

WORKDIR ${HOME}
ADD . ${HOME}

# Install tests dependencies
RUN pip2 install -r requirements.txt
# Install
RUN python2 setup.py install

# Create a user
RUN useradd bitmessage && chown -R bitmessage ${HOME}

USER bitmessage

# Clean HOME
RUN rm -rf ${HOME}/*

# Generate default config
RUN pybitmessage -t

# Setup environment
RUN APIPASS=$(tr -dc a-zA-Z0-9 < /dev/urandom | head -c32 && echo) \
  && echo "\napiusername: api\napipassword: $APIPASS" \
  && echo "apienabled = true\napiinterface = 0.0.0.0\napiusername = api\napipassword = $APIPASS" >> keys.dat

CMD ["pybitmessage", "-d"]
