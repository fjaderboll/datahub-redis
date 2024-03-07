# Docker setup

## Build
```shell
./app/build.sh   # build image 'datahub-app'
./web/build.sh   # build image 'datahub-web'
./emqx/build.sh  # build image 'datahub-emqx'
docker image ls | grep datahub
```

## Deploy

```shell
cp stack.yaml.default stack.yaml
vi stack.yaml                                         # modify ports, passwords, persistence, etc, to your liking
docker stack deploy --compose-file stack.yaml datahub # deploy
docker stack rm datahub                               # un-deploy
```

* Go to [http://localhost:2084/](http://localhost:8080/) for Web UI.
* Go to [http://localhost:2084/api](http://localhost:8080/api) for Swagger doc.
