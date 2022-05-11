FROM ubuntu:xenial

RUN apt-get update

# Common apt packages
RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    software-properties-common build-essential libcap-dev libffi-dev \
    libssl-dev python-all-dev python-pip python-setuptools python3-dev

# wget
RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    libgmp-dev m4 pkgconf wget

RUN wget "https://ftp.gnu.org/gnu/nettle/nettle-3.9.1.tar.gz" \
    && tar -zxf nettle-3.9.1.tar.gz

RUN cd nettle-3.9.1 \
    && ./configure --disable-openssl --enable-shared \
    && make && make install

RUN wget "https://www.gnupg.org/ftp/gcrypt/gnutls/v3.6/gnutls-3.6.16.tar.xz" \
    && tar -Jxf gnutls-3.6.16.tar.xz

RUN apt-get remove -yq libgnutls30

RUN cd gnutls-3.6.16 \
    && ./configure --prefix=/usr --without-p11-kit \
    --with-included-libtasn1 --with-included-unistring --without-idn \
    && make && make install

RUN wget "https://ftp.gnu.org/gnu/wget/wget2-2.1.0.tar.gz" \
    && tar -zxf wget2-2.1.0.tar.gz

RUN apt-get remove -yq wget

RUN cd wget2-2.1.0 \
    && ./configure --without-libpsl --prefix=/usr \
    GNUTLS_CFLAGS=-I/usr/include/gnutls/ GNUTLS_LIBS=-L/usr/lib \
    && make && make install \
    && mv /usr/bin/wget2 /usr/bin/wget

RUN wget -O /usr/local/bin/buildbot_entrypoint.sh http://git.bitmessage.org/Bitmessage/buildbot-scripts/raw/branch/master/docker/xenial/entrypoint.sh

RUN pip install --upgrade pip==20.0.1
RUN pip install --upgrade setuptools
RUN pip install tox

ADD . .

CMD .buildbot/tox-xenial/test.sh
