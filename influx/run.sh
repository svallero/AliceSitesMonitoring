#!/bin/sh

docker run -p 8086:8086 -v influxdb:/var/lib/influxdb \
          --rm --name influxdb \
          -d influxdb:1.8

#          -e DOCKER_INFLUXDB_INIT_MODE=setup \
#          -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
#          -e DOCKER_INFLUXDB_INIT_PASSWORD=pippo123 \
#          -e DOCKER_INFLUXDB_INIT_ORG=alice \
#          -e DOCKER_INFLUXDB_INIT_BUCKET=alice \
