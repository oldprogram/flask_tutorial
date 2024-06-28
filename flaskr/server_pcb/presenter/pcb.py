from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify
from werkzeug.exceptions import abort

from flaskr.server_auth.presenter.auth import login_required
from flaskr.db import get_db

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# https://stackoverflow.com/questions/38220574/render-template-from-flask-blueprint-uses-other-blueprints-template
# 指定蓝图搜索空间，但是会被覆盖
bp = Blueprint("pcb", __name__ ,url_prefix="/pcb",static_folder='../view', template_folder="../view")


@bp.route("/")
def index():
    # 查询所有分类
    results = (
        get_db()
        .execute(
            "SELECT name FROM category",
        )
        .fetchall()
    )

    categories = [tuple(row)[0] for row in results]
    #print(categories)


    # 查询所有 pcb 的 id, name 和所包含的 categories 的 name
    query = """
    SELECT p.id, p.name, GROUP_CONCAT(c.name, ', ') as categories
    FROM pcb p
    LEFT JOIN pcb_category pc ON p.id = pc.pcb_id
    LEFT JOIN category c ON pc.category_id = c.id
    GROUP BY p.id, p.name
    ORDER BY p.created DESC
    """
    results = (
        get_db()
        .execute(query)
        .fetchall()
    )
   
    #productsx = [tuple(row) for row in results]   
    #print(productsx)
    #print(jsonify(productsx).get_data(as_text=True))
    products = []
    for row in results:
        t_row = tuple(row)
        products.append({'url': f'product{t_row[0]}.html', 'space': f'pcb_{t_row[0]}', 'name': t_row[1], 'category': t_row[2], 'views': 1000})

    '''
    products = [
        {'url': 'product1.html', 'space': 'pcb_1', 'name': '商品名称1', 'category': '电子产品', 'views': 1000},
        {'url': 'product2.html', 'space': 'pcb_2', 'name': '商品名称2', 'category': '服装', 'views': 1500},
        {'url': 'product3.html', 'space': 'pcb_3', 'name': '商品名称3', 'category': '家居用品', 'views': 2000},
        # 继续添加更多商品
    ]
    '''
    return render_template("pcb_html/index.html", categories=categories, products=products)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new pcb for the current user."""
    if request.method == "POST":
        #print(request.form)
        name = request.form["name"]
        categories = request.form["selectedCategories"]

        error = None
        
        if 'imageUpload' not in request.files:
            error = "Image is required."
        file = request.files['imageUpload']
        if file and file.filename == '' and file.filename.endswith('.png'):
            error = "No select image."

        if not name:
            error = "Name is required."

        if error is not None:
            print(error)
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO pcb (name, author_id) VALUES (?, ?)",
    (name, g.user["id"]),
            )

            # 获取新插入的 pcb 的 id
            pcb_id = cursor.lastrowid

            # 将 categories 字符串分割成列表
            category_names = categories.split(',')
            # 遍历每个分类名，查询 category_id 并插入 pcb_category 表
            for category_name in category_names:
                category_name = category_name.strip()  # 去除多余的空格
                cursor.execute(
                    "SELECT id FROM category WHERE name = ?",
                    (category_name,)
                )
                category_id = cursor.fetchone()
                if category_id:
                    cursor.execute(
                        "INSERT INTO pcb_category (pcb_id, category_id) VALUES (?, ?)",
                        (pcb_id, category_id[0])
                    )

            db.commit()

            # 将文件存储，主要是封面
            file.filename = "cover.png" 
            file_path = basedir+f"/../view/pcb_static/products/pcb_{pcb_id}/pics" 
            # 如果文件夹不存在，就创建文件夹
            if not os.path.exists(file_path):
	            os.makedirs(file_path)
            file.save(os.path.join(file_path, file.filename))

            return redirect(url_for("pcb.index"))

    return render_template("pcb_html/create.html")


#############################################################################
# 标签相关
#############################################################################
@bp.route("/create/get_categories", methods=["GET"])
@login_required
def get_categories():
    if request.method == "GET":
        results = (
            get_db()
            .execute(
                "SELECT name FROM category",
            )
            .fetchall()
        )
        
        results = [tuple(row) for row in results]
        #print(results)
        return jsonify(results)

@bp.route("/create/add_category", methods=["POST"])
@login_required
def add_category():
    if request.method == "POST":
        category = request.json.get("category")
        if category:
            db = get_db()
            db.execute(
                "INSERT INTO category (name) VALUES (?)",
                (category,),
            )
            db.commit()

            #print(f"Added category: {category}")
            return jsonify({"message": "Category added successfully"})
        else:
            return jsonify({"error": "Category parameter missing"}), 400


