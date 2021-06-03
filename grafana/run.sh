#!/bin/sh

docker run -d --name=grafana -p 3000:3000 \
           --rm -v $PWD/data:/var/lib/grafana \
           grafana/grafana
