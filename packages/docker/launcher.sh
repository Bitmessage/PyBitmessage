#!/bin/sh

# Setup the environment for docker container
APIUSER=${USER:-api}
APIPASS=${PASSWORD:-$(tr -dc a-zA-Z0-9 < /dev/urandom | head -c32 && echo)}
IP=$(hostname -i)

echo "\napiusername: $APIUSER\napipassword: $APIPASS"

sed -i -e "s|\(apiinterface = \).*|\1$IP|g" \
    -e "s|\(apivariant = \).*|\1json|g" \
    -e "s|\(apiusername = \).*|\1$APIUSER|g" \
    -e "s|\(apipassword = \).*|\1$APIPASS|g" \
    -e "s|\(bind = \).*|\1$IP|g" \
    -e "s|apinotifypath = .*||g" ${BITMESSAGE_HOME}/keys.dat

# Run
exec pybitmessage "$@"
