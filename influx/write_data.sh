#!/bin/sh

now=`date +%s000000000`
string="wall,site=test locale=1234,monalisa=1235,egi=1236 $now"

#echo $string
curl -i -XPOST 'http://localhost:8086/write?db=alice' --data-binary "$string"
