#!/bin/bash
#
# Subscribes to a dataset, inserts readings alternating between MQTT and HTTP,
# and checks that all of them are published on MQTT. See README.md.

set -eo pipefail

host=localhost
api_url="http://$host:8080/api"
mqtt_port=1883
nodes=(kitchen bedroom garage)
sensors=(temperature humidity pressure)
timeout=5 # seconds to wait for the last readings after inserting

user=admin
pass=secret
dataset=test
count=10

usage() {
	cat <<-EOF
	Usage: $(basename "$0") [options]

	  -u, --user USER      username, registered if missing (default: $user)
	  -p, --pass PASS      password (default: $pass)
	  -d, --dataset NAME   dataset, created if missing (default: $dataset)
	  -c, --count N        number of readings to insert (default: $count)
	  -h, --help           show this help
	EOF
}

while [ $# -gt 0 ]; do
	case "$1" in
		-u|--user)    user="$2"; shift 2 ;;
		-p|--pass)    pass="$2"; shift 2 ;;
		-d|--dataset) dataset="$2"; shift 2 ;;
		-c|--count)   count="$2"; shift 2 ;;
		-h|--help)    usage; exit 0 ;;
		*)            usage >&2; exit 1 ;;
	esac
done

if ! [[ "$count" =~ ^[1-9][0-9]*$ ]]; then
	echo "Count must be a positive number" >&2
	exit 1
fi

# POSTs JSON to the REST API and prints the response,
# or prints the error message to stderr and returns 1
token=
post() {
	local auth=() response message
	if [ -n "$token" ]; then
		auth=(-H "Authorization: Bearer $token")
	fi
	if ! response=$(curl -s --fail-with-body -X POST "$api_url/$1" \
			-H 'Content-Type: application/json' "${auth[@]}" -d "$2"); then
		message=$(jq -r '.message // empty' <<< "$response" 2>/dev/null)
		echo "  ${message:-Request failed: POST $api_url/$1}" >&2
		return 1
	fi
	echo "$response"
}

echo "Registering user '$user'"
post users/ "$(jq -nc --arg u "$user" --arg p "$pass" '{username: $u, password: $p}')" > /dev/null || true

echo "Logging in"
token=$(post "users/$user/login" "$(jq -nc --arg p "$pass" '{password: $p}')" | jq -r .token)

echo "Creating MQTT only token"
mqtt_token=$(post tokens/ '{"desc": "test.sh", "ttl": 600, "mqttOnly": true}' | jq -r .token)

echo "Creating dataset '$dataset'"
post datasets/ "$(jq -nc --arg n "$dataset" '{name: $n}')" > /dev/null || true

topic="out/datasets/$dataset/#"
echo "Subscribing to '$topic'"
mosquitto_sub -h $host -p $mqtt_port -u "$user" -P "$mqtt_token" -v -C $count -t "$topic" &
sub_pid=$!
trap 'kill $sub_pid 2>/dev/null || true' EXIT
sleep 1 # give it time to connect and subscribe
if ! kill -0 $sub_pid 2>/dev/null; then
	echo "Unable to subscribe, check that user '$user' has access to dataset '$dataset'?" >&2
	exit 1
fi

echo "Inserting $count readings, alternating between MQTT and HTTP"
for ((i = 0; i < count; i++)); do
	node=${nodes[i % ${#nodes[@]}]}
	sensor=${sensors[i / ${#nodes[@]} % ${#sensors[@]}]}
	value="$((RANDOM % 100)).$((RANDOM % 10))"
	path="datasets/$dataset/nodes/$node/sensors/$sensor/readings"

	if ((i % 2 == 0)); then
		mosquitto_pub -h $host -p $mqtt_port -u "$user" -P "$mqtt_token" -t "in/$path" -m "{\"value\": $value}"
	else
		post "$path" "[{\"value\": $value}]" > /dev/null
	fi
done

# the subscriber exits by itself once it has received all readings
for ((i = 0; i < timeout * 10; i++)); do
	kill -0 $sub_pid 2>/dev/null || break
	sleep 0.1
done
kill $sub_pid 2>/dev/null || true
if wait $sub_pid; then
	echo "All $count readings received"
else
	echo "Not all $count readings were received within $timeout seconds" >&2
	exit 1
fi
