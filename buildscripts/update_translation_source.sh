#!/bin/sh

xgettext -Lpython --output=src/translations/messages.pot \
src/bitmessagekivy/mpybit.py src/bitmessagekivy/main.kv \
src/bitmessagekivy/baseclass/*.py src/bitmessagekivy/kv/*.kv
