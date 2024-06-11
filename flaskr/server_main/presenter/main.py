from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.server_auth.presenter.auth import login_required
from flaskr.db import get_db

# https://stackoverflow.com/questions/22152840/flask-blueprint-static-directory-does-not-work
# 让蓝图具备独立 static 文件夹
bp = Blueprint("main", __name__ , static_folder='../view', template_folder="../view")


@bp.route("/")
def index():
    return render_template("main.html")
