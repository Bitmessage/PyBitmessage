#!/bin/sh
echo "Script executed from1: ${PWD}"

mkdir -p ../out

cd pybitmessage/bitmessagekivy

xgettext -Lpython --output=../../../out/messages.pot mpybit.py main.kv ./baseclass/*.py ./kv/*.kv

curl https://www.transifex.com/bitmessage-project/pybitmessage/upload_source/$BUILDBOT_JOBID

# curl https://www.transifex.com/bitmessage-project/pybitmessage-test/$BUILDBOT_JOBID