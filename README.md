# datahub (Redis version)

## About
A fast database with a Web UI to hold your IoT data.
Use the REST API to store and retrieve time series
of numbers or use the built-in MQ broker to publish
or subscribe to your data.

## Background
I have many IoT devices generating data and need to store that
data somewhere. After searching I did not find any existing
projects or free/cheap services the offered the simplicity I
was looking for so I decided to write my own IoT database.

## History
This is a re-design of my previous project [datahub](https://github.com/fjaderboll/datahub), which is based on SQLite and PHP.
Check that out if you want something that can be deployed simply on a web server.

## Quick start
Everything runs in a single container:
```shell
docker run \
	-d \
	--name datahub \
	--restart unless-stopped \
	-p 8080:8080 \
	-p 1883:1883 \
	-v datahub-data:/data \
	ghcr.io/fjaderboll/datahub:latest
```

* Navigate to [http://localhost:8080/](http://localhost:8080/) and create the first user, which becomes administrator.
* REST API documentation (Swagger) is at [http://localhost:8080/api/](http://localhost:8080/api/).
* The MQTT broker is at `localhost:1883`, log in with your datahub username and password.
	- Publish readings to a dataset you have created, for example
  `in/datasets/home/nodes/kitchen/sensors/temperature/readings` with `{"value": 21.5}`,
	- Subscribe to `out/datasets/home/#` to get them pushed to you.

## Overview
![overview](doc/overview.png)

### Storage
Readings are stored in [Redis](https://redis.io/) time series, which keeps them in memory
for fast access and avoids unnecessary disk writes.
Users, datasets, nodes and sensors are stored in [SQLite](https://www.sqlite.org/).


### Entities
Structure of entities with examples:

![entities](doc/entities.png)

## File structure

* [app](app/README.md) - The application backend (where it all happens)
* [web](web/README.md) - The web frontend (administration and viewing data)
* [docker](docker/README.md) building the image yourself.
