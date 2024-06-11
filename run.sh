#!/usr/bin/env python
# coding=utf-8

#python3.9 -m venv venv
#pip install flask
#pip install python_avatars
#pip install pypinyin
. ./venv/bin/activate

export FLASK_APP=flaskr
export FLASK_ENV=development
#flask init-db
flask run --host=0.0.0.0 --port=5000
