# App - backend

## Doc

* https://redis.io/docs/latest/develop/data-types/timeseries/
* https://redis-py.readthedocs.io/en/stable/examples/timeseries_examples.html
* https://www.sqlite.org/lang.html

## Setup
Requires Python 3.10 or newer (the Docker image uses Python 3.15).

```shell
sudo apt install python3-venv python3-pip docker.io
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Database
Data is split between two databases:
* **SQLite** holds users, tokens, settings, datasets, nodes and sensors.
  The file is `app/datahub.db` by default, set `SQLITE_PATH` to change it.
  It is created on first start.
* **Redis** (with its built-in time series support) holds the readings,
  one time series per sensor with the key `sensor-readings:<sensor id>`.

```shell
docker run -d --rm --name datahub-redis -p 6379:6379 -v datahub-redis-data:/data redis:8.10.2
docker exec -it datahub-redis redis-cli   # interact with Redis
sqlite3 datahub.db                        # interact with SQLite
```

### Maintenance
Run from the `src` folder (or `docker exec -u datahub datahub python3 maintenance.py ...`):
```shell
python3 maintenance.py check               # compare sensors in SQLite with time series in Redis
python3 maintenance.py repair              # create missing time series and delete orphaned ones
```

## MQ broker
NanoMQ checks logins and topic permissions with the app (`/api/mqtt/authenticate` and `/api/mqtt/authorize`),
here running on the host at port 8080:

```shell
docker run \
	-d \
	--rm \
	--name datahub-nanomq \
	-p 1883:1883 \
	--add-host=host.docker.internal:host-gateway \
	-v $PWD/../docker/nanomq.dev.conf:/etc/nanomq.conf \
	emqx/nanomq:0.25.6-slim
```

## Application
Always activate the virtual environment first:
```shell
source .venv/bin/activate
```

### Run
From within Visual Studio Code you can use the `launch.json` file.
Make sure the Redis database and NanoMQ is running.

```shell
flask --app src/app.py --debug run --port 8080               # development
gunicorn --workers 4 --bind 0.0.0.0:8080 -k gevent wsgi:app  # production
```

The API is served under `/api` (Swagger doc at `/api/`) and, if built, the web frontend
from `web/dist/web` (set `WEB_PATH` to change it) at `/`.

### Add new dependency

```shell
pip3 install flask-restx
pip3 freeze | grep flask-restx== >> requirements.txt
```

### Upgrading dependencies

```shell
source .venv/bin/activate
pip3 install pip-upgrader
pip-upgrade  # enter 'all' to update requirements.txt
```

### Test
Tests are located in `test` folder.
Tests files must contain `test` to be discovered.

```shell
BASE_URL=http://localhost:8080/api/ python3 -m unittest discover -s test -vv
```
