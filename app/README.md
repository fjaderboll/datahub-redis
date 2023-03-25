# App - backend

## Doc

* https://redis.io/docs/getting-started/
* https://redis.io/docs/stack/timeseries/


## Setup

```shell
sudo apt install python3-venv python3-pip docker.io
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Database

```shell
docker run -d --rm --name redis -p 6379:6379 redis:7  # start
docker exec -it redis redis-cli                       # interact with database
```

## Application
Always activate the virtual environment first:
```shell
source .venv/bin/activate
```

### Run
```shell
./app.py 2070    # start server at http://localhost:2070/
```

### Add new dependency

```shell
pip3 install flask
pip3 freeze > requirements.txt
```

### Test

```shell
python -m unittest discover -s test
```
