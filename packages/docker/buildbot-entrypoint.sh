#!/bin/bash


buildbot-worker create-worker /var/lib/buildbot/workers/default "$1" "$2" "$3"

unset BUILDMASTER BUILDMASTER_PORT WORKERNAME WORKERPASS

cd /var/lib/buildbot/workers/default
/usr/bin/dumb-init buildbot-worker start --nodaemon
