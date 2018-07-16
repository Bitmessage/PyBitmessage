# A container for PyBitmessage daemon

FROM ubuntu:xenial

RUN apt-get update

# Install dependencies
RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    python-msgpack dh-python python-all-dev build-essential libssl-dev \
    python-stdeb fakeroot python-pip libcap-dev

RUN pip install --upgrade pip

EXPOSE 8444 8442

ENV HOME /home/bitmessage
ENV BITMESSAGE_HOME ${HOME}

ENV VER 0.6.3.2

WORKDIR ${HOME}
ADD . ${HOME}

# Install tests dependencies
RUN pip install -r requirements.txt

# Build and install deb
RUN python2 setup.py sdist \
  && py2dsc-deb dist/pybitmessage-${VER}.tar.gz \
  && dpkg -i deb_dist/python-pybitmessage_${VER}-1_amd64.deb

# Generate default config
RUN src/bitmessagemain.py -t && mv keys.dat ..

# Clean HOME
RUN rm -rf ${HOME}

# Setup environment
RUN mv ../keys.dat . \
  && APIPASS=$(tr -dc a-zA-Z0-9 < /dev/urandom | head -c32 && echo) \
  && echo "\napiusername: api\napipassword: $APIPASS" \
  && echo "apienabled = true\napiinterface = 0.0.0.0\napiusername = api\napipassword = $APIPASS" >> keys.dat

CMD ["pybitmessage", "-d"]
