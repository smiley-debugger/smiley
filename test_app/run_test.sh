#!/bin/sh

cd $(dirname $0)
smiley --debug -v run --local --database ../smiley.db -- test.py $@
