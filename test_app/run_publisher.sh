#!/bin/sh

cd $(dirname $0)
smiley --debug -vvvv run --remote -- test.py
