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
Run from the `src` folder (or `docker exec <app container> python3 maintenance.py ...`):
```shell
python3 maintenance.py check               # compare sensors in SQLite with time series in Redis
python3 maintenance.py repair              # create missing time series and delete orphaned ones
python3 maintenance.py remove-legacy-keys  # delete data left in Redis by the Redis-only version
```

### Upgrading from the Redis-only version
When the application starts with an empty SQLite database and Redis still contains
users, datasets, nodes and sensors from the Redis-only version, these are imported
automatically. Ids are kept, so the existing readings stay connected to their sensors.
Orphaned entries are skipped and duplicates (such as two sensors with the same name on
the same node) are merged; everything skipped or merged is logged as a warning.
Once the application works as expected, run `maintenance.py check` followed by
`maintenance.py remove-legacy-keys`.

## MQ broker

```shell
docker run \
	-d \
	--rm \
	--name datahub-emqx \
	-p 18083:18083 \
	-p 1883:1883 \
	-v $PWD/../docker/emqx/cluster.hocon.local:/opt/emqx/data/configs/cluster.hocon \
	-e "EMQX_dashboard__default_username=admin" \
    -e "EMQX_dashboard__default_password=admin123" \
	emqx:5.5.0
	#-e "EMQX_AUTHENTICATION__1__URL=http://172.16.1.5:2070/mqtt/authenticate" \
    #-e "EMQX_AUTHORIZATION__SOURCES__1__URL=http://172.16.1.5:2070/mqtt/authorize" \
```

## Application
Always activate the virtual environment first:
```shell
source .venv/bin/activate
```

### Run
From within Visual Studio Code you can use the `launch.json` file.

```shell
flask --app src/app.py --debug run                           # development (preferred way)
#./src/app.py 2070                                           # development
gunicorn --workers 4 --bind 0.0.0.0:2070 -k gevent wsgi:app  # production
```

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
BASE_URL=http://localhost:2070/ python3 -m unittest discover -s test -vv
```
