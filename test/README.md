# Test

## Simple test
Whether you use HTTP or MQTT to insert new readings, they'll
still be published on the MQTT.

[test.sh](test.sh) tests this by subscribing to a dataset, then
inserting readings spread across a few nodes and sensors, alternating
between MQTT and HTTP, and checking that all of them are received.
It needs `mosquitto_sub`/`mosquitto_pub` (from the `mosquitto-clients` package),
`curl` and `jq`.

```shell
./test.sh [-u|--user USER] [-p|--pass PASS] [-d|--dataset NAME] [-c|--count N]
```

The user (default `admin` with password `secret`) and the dataset
(default `test`) are created if they don't exist. Registering the user requires that
it's the first user or that public registration is enabled.

Example output:
```shell
$ ./test.sh -c 4
Registering user 'admin'
  Username 'admin' already exists
Logging in
Creating MQTT only token
Creating dataset 'test'
  Dataset 'test' already exists
Subscribing to 'out/datasets/test/#'
Inserting 4 readings, alternating between MQTT and HTTP
out/datasets/test/nodes/kitchen/sensors/temperature/readings {"timestamp": "2026-10-24T16:43:49.407000+00:00", "value": 76.3, "datasetName": "test", "nodeName": "kitchen", "sensorName": "temperature", "unit": ""}
out/datasets/test/nodes/bedroom/sensors/temperature/readings {"timestamp": "2026-10-24T16:43:49.411000+00:00", "value": 17.6, "datasetName": "test", "nodeName": "bedroom", "sensorName": "temperature", "unit": ""}
out/datasets/test/nodes/garage/sensors/temperature/readings {"timestamp": "2026-10-24T16:43:49.422000+00:00", "value": 29.6, "datasetName": "test", "nodeName": "garage", "sensorName": "temperature", "unit": ""}
out/datasets/test/nodes/kitchen/sensors/humidity/readings {"timestamp": "2026-10-24T16:43:49.427000+00:00", "value": 59.2, "datasetName": "test", "nodeName": "kitchen", "sensorName": "humidity", "unit": ""}
All 4 readings received
```

## Performance
[performance.py](performance.py) measures how long it takes to insert readings
over HTTP (one reading per request, and all in one request) and over MQTT
(one reading per message, until all are published back out), and to load them.
Each is run 3 times and the median is reported.
It needs Python with `requests` and `mosquitto_sub`/`mosquitto_pub`.

```shell
./performance.py [-u|--user USER] [-p|--pass PASS] [-d|--dataset NAME] [-c|--count N]
```

The user and dataset are created as for `test.sh`, and `--count` defaults to 10000.
The readings are put in the node `performance`, which is removed afterwards.
If the dataset already has a node with that name, nothing is run.

Example output (end of it):
```shell
$ ./performance.py
...
Median of 3 runs, inserting 10000 readings:
  HTTP, one reading per request         24.162 seconds (414 readings/s)
  HTTP, all readings in one request      4.314 seconds (2318 readings/s)
  MQTT, one reading per message          9.511 seconds (1051 readings/s)
Median of 45 loads, loading 10000 readings:
  HTTP, all readings in one request      0.049 seconds (204903 readings/s)
Removing node 'performance'
```
