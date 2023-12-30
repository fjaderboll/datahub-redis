#!/bin/bash -e

cd $(dirname "${BASH_SOURCE[0]}")

options=
if [ "$1" = "-c" ]; then
    options="--no-cache"
fi

mkdir -p tmp
cp -r ../../app/src tmp/
rm -fr `find tmp/ -type d -name __pycache__`
cp ../../app/requirements.txt tmp/.
docker build ${options} -t datahub-app .
rm -r tmp
