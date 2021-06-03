#!/bin/sh

curl -i -XPOST 'http://localhost:8086/query' -d "db=alice" -d "q=drop measurement jobResUsageSum_time_run"
