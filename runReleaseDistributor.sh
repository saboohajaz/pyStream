#!/bin/bash

export FLASK_APP=distributor
export FLASK_ENV=production
export FLASK_RUN_HOST=10.1.1.254
export FLASK_RUN_PORT=5000

python3 distributor.py --host=10.1.1.254
