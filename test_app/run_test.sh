#!/bin/sh

cd $(dirname $0)
echo "testing..."
smiley --debug -v run --local --database ../smiley.db -- test.py $@
