#!/bin/bash

exec newrelic-admin run-program celery -A kitsune beat -l INFO
