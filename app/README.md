# App - backend

## Doc

* https://redis.io/docs/getting-started/
* https://redis.io/docs/stack/timeseries/
* https://redis-py.readthedocs.io/en/stable/examples/timeseries_examples.html

## Setup

```shell
sudo apt install python3-venv python3-pip docker.io
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Database

```shell
docker run -d --rm --name datahub-redis -p 6379:6379 -v datahub-redis-data:/data redislabs/redistimeseries:1.10.11
docker exec -it datahub-redis redis-cli   # interact with database
```

## MQ broker

```shell
docker run -d --rm --name emqx -p 18083:18083 -p 1883:1883 emqx:5.5.0
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

### Test
Tests are located in `test` folder.
Tests files must contain `test` to be discovered.

```shell
BASE_URL=http://localhost:2070/ python3 -m unittest discover -s test -vv
```
