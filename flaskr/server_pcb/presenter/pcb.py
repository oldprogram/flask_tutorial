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


# https://stackoverflow.com/questions/38220574/render-template-from-flask-blueprint-uses-other-blueprints-template
# 指定蓝图搜索空间，但是会被覆盖
bp = Blueprint("pcb", __name__ ,url_prefix="/pcb",static_folder='../view', template_folder="../view")


@bp.route("/")
def index():
    categories = ['电子产品', '服装', '家居用品', '运动户外', '美妆个护']
    products = [
        {'url': 'product1.html', 'space': 'pcb_0', 'name': '商品名称1', 'category': '电子产品', 'views': 1000},
        {'url': 'product2.html', 'space': 'pcb_1', 'name': '商品名称2', 'category': '服装', 'views': 1500},
        {'url': 'product3.html', 'space': 'pcb_2', 'name': '商品名称3', 'category': '家居用品', 'views': 2000},
        # 继续添加更多商品
    ]
    return render_template("pcb_html/index.html", categories=categories, products=products)


