#!/bin/bash

py.test -s --cov-report term-missing --cov-config tests/.coveragerc --cov app tests/