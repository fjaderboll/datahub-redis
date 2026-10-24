# Docker setup

## Build
```shell
./app/build.sh   # build image 'datahub-app'
./web/build.sh   # build image 'datahub-web'
./emqx/build.sh  # build image 'datahub-emqx'
docker image ls | grep datahub
```

## Deploy
Redis holds the readings and SQLite (in the `app-data` volume) holds everything else.

```shell
cp stack.yaml.default stack.yaml
vi stack.yaml                                         # modify ports, passwords, persistence, etc, to your liking
docker stack deploy --compose-file stack.yaml datahub # deploy
docker stack rm datahub                               # un-deploy
```

### Upgrading from the Redis-only version
1. Back up the `redis-data` volume. Redis 8 rewrites the data file, which older Redis versions may not be able to read.
2. Update your `stack.yaml` from `stack.yaml.default`: the `redis` image and command, and the new `app-data` volume for `app`.
3. Deploy. On first start the app imports users, datasets, nodes and sensors from Redis into SQLite and logs a summary (`docker service logs datahub_app`).
4. Verify in the Web UI, then clean up:
   ```shell
   docker exec $(docker ps -qf name=datahub_app) python3 maintenance.py check
   docker exec $(docker ps -qf name=datahub_app) python3 maintenance.py remove-legacy-keys
   ```

* Go to [http://localhost:2084/](http://localhost:8080/) for Web UI.
* Go to [http://localhost:2084/api](http://localhost:8080/api) for Swagger doc.
