#!/bin/bash

if [ -z "$1" ]; then
	echo "You must specify pull request number"
	exit
fi

git pull
git checkout v0.6
git fetch origin pull/"$1"/head:"$1"
git merge --ff-only "$1"
