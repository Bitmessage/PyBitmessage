#!/bin/sh

# Setup the environment for docker container
APIUSER=${USER:-api}
APIPASS=${PASSWORD:-$(tr -dc a-zA-Z0-9 < /dev/urandom | head -c32 && echo)}

echo "\napiusername: $APIUSER\napipassword: $APIPASS"

sed -i -e "s|\(apiinterface = \).*|\10\.0\.0\.0|g" \
    -e "s|\(apivariant = \).*|\1json|g" \
    -e "s|\(apiusername = \).*|\1$APIUSER|g" \
    -e "s|\(apipassword = \).*|\1$APIPASS|g" \
    -e "s|apinotifypath = .*||g" ${BITMESSAGE_HOME}/keys.dat

if [ -n "$PYBITMESAGE_BOOTSTRAP" -o -n "$PYBITMESSAGE_TESTNET" ]; then
    echo "[bootstrap]" >> ${BITMESSAGE_HOME}/keys.dat
fi

if [ -n "$PYBITMESSAGE_BOOTSTRAP" ]; then
    IP=$(hostname -i)
    sed -i -e "s|\(apiinterface = \).*|\1$IP|g" \
        -e "s|\(bind = \).*|\1$IP|g" \
        ${BITMESSAGE_HOME}/keys.dat
    echo <<(EOF) >> ${BITMESSAGE_HOME}/keys.dat
idle_timeout = 60
commands = True
threads = True
inv = True
dup_ip = True
(EOF)
fi

if [ -n "$PYBITMESSAGE_TESTNET" ]; then
    IP=$(hostname -i)
    sed -i -e "s|\(apiinterface = \).*|\1$IP|g" \
        -e "s|\(bind = \).*|\1$IP|g" \
        ${BITMESSAGE_HOME}/keys.dat
    echo <<(EOF) >> ${BITMESSAGE_HOME}/keys.dat
testnet = True
(EOF)
fi

# Run
exec pybitmessage "$@"
