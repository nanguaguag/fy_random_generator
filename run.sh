#!/bin/bash

export FLASK_APP=app.py
nohup flask run -p 5001 > flask.log 2>&1 &

