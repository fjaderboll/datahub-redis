#!/bin/bash -e

cd $(dirname "${BASH_SOURCE[0]}")

REMOTE_HOST=panther.lan

build() {
	./$1/build.sh
}
package() {
	docker save -o /tmp/image_datahub-$1.tar datahub-$1
	if [ -f /tmp/image_datahub-$1.tar.gz ]; then
		rm /tmp/image_datahub-$1.tar.gz
	fi
	gzip -v --fast /tmp/image_datahub-$1.tar
}
load() {
	ssh $REMOTE_HOST gunzip -v /tmp/image_datahub-$1.tar.gz
	ssh $REMOTE_HOST docker load -i /tmp/image_datahub-$1.tar
	ssh $REMOTE_HOST rm /tmp/image_datahub-$1.tar
}

build app
build web
build emqx

ssh $REMOTE_HOST docker stack rm datahub

package app
package web
package emqx

scp stack.yaml /tmp/image_datahub-*.tar.gz $REMOTE_HOST:/tmp/.

load app
load web
load emqx

ssh $REMOTE_HOST docker stack deploy --compose-file /tmp/stack.yaml datahub
ssh $REMOTE_HOST rm /tmp/stack.yaml
