# Docker setup
Everything runs in a single image: the app (which also serves the web frontend),
Redis holding the readings and the [NanoMQ](https://nanomq.io/) MQTT broker.
[s6-overlay](https://github.com/just-containers/s6-overlay) starts them in order,
restarts them if they stop and stops them in reverse order, see [rootfs/etc/s6-overlay](rootfs/etc/s6-overlay/s6-rc.d).

GitHub Actions builds the image for amd64 and arm64 on every push and publishes it to `ghcr.io/fjaderboll/datahub-redis`,
tagged `latest` (master), with the branch name and with the version of `v*` tags.

## Build
```shell
./build.sh      # build image 'datahub'
./build.sh -c   # clean build (without cache)
```

## Run
```shell
docker run -d --name datahub -p 8080:8080 -p 1883:1883 -v datahub-data:/data datahub
```

* Go to [http://localhost:8080/](http://localhost:8080/) for Web UI.
* Go to [http://localhost:8080/api/](http://localhost:8080/api/) for Swagger doc.
* Connect to `localhost:1883` for MQTT.

| Environment variable | Description |
| --- | --- |
| `TZ` | Time zone, default `Europe/Stockholm` |
| `MQTT_USERNAME`, `MQTT_PASSWORD` | The app's own MQTT account, default `mqtt` with a random password. Set the password to use the account from elsewhere, it may subscribe to all `in/...` topics and publish to all `out/...` topics |

Everything is stored in `/data`:
* `datahub.db` - SQLite database with users, datasets, nodes and sensors
* `redis/dump.rdb` - Redis snapshot with the readings, saved once a day (every 6 hours with many changes) and when the container is stopped

A crash or `docker kill` loses the readings since the last snapshot. With a large dataset, give Redis more time to save
on stop than Docker's default 10 seconds, e.g. `docker run --stop-timeout 30 ...`.

Maintenance and database access:
```shell
docker exec -u datahub datahub python3 maintenance.py check   # see app/README.md
docker exec -it -u datahub datahub sqlite3 /data/datahub.db
docker exec -it datahub redis-cli
```
