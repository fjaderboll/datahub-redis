#!/bin/bash -e

cd $(dirname "${BASH_SOURCE[0]}")

options=
if [ "$1" = "-c" ]; then
    options="--no-cache"
fi

mkdir -p tmp
pushd ../../web
rm -r dist/web
npm run build
popd
cp -r ../../web/dist/web tmp/
docker build ${options} -t datahub-web .
rm -r tmp
