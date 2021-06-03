#!/bin/sh
curl -X POST -G http://localhost:8086/query  --data-urlencode "q=CREATE DATABASE alice" 
#curl -X POST -G http://localhost:8086/query  --data-urlencode "q=SHOW DATABASES"

