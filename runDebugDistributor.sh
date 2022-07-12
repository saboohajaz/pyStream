#!/bin/bash

export FLASK_APP=distributor
export FLASK_ENV=development
export FLASK_RUN_HOST=127.0.0.1
export FLASK_RUN_PORT=5000

python3 distributor.py
