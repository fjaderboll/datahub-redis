# Docker setup

## Build
```shell
./app/build.sh   # build image 'datahub-app'
./web/build.sh   # build image 'datahub-web'
docker image ls | grep datahub
```

## Deploy
```shell
docker stack deploy --compose-file stack.yaml datahub
docker stack rm datahub
```
