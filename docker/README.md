# Docker setup

## Build
```shell
./app/build.sh   # build image 'datahub-app'
./web/build.sh   # build image 'datahub-web'
docker image ls | grep datahub
```

## Deploy
Look in `stack.yaml` to change the exposed port number.

```shell
docker stack deploy --compose-file stack.yaml datahub # deploy
docker stack rm datahub                               # un-deploy
```

* Go to [http://localhost:2084/](http://localhost:2084/) for Web UI.
* Go to [http://localhost:2084/api](http://localhost:2084/api) for Swagger doc.
