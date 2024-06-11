#!/usr/bin/env python
# coding=utf-8

. ./venv/bin/activate

export FLASK_APP=flaskr
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
