#!/usr/bin/env python
# coding=utf-8

import os
import random
from datetime import datetime
from flask import Blueprint
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory
from flask import render_template
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = basedir+'/static/file/img'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("tuchuang", __name__, url_prefix="/tuchuang")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # 获取安全的文件名 正常文件名
            filename = secure_filename(file.filename)
            
            # 生成随机数
            random_num = random.randint(0, 100)
            # f.filename.rsplit('.', 1)[1] 获取文件的后缀
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random_num) + "." + filename.rsplit('.', 1)[1]
            file_path = app.config['UPLOAD_FOLDER']    # basedir 代表获取当前位置的绝对路径
            
            # 如果文件夹不存在，就创建文件夹
            if not os.path.exists(file_path):
	            os.makedirs(file_path)
	
            file.save(os.path.join(file_path, filename))
            return redirect(url_for('tuchuang.download_file', name=filename))
    return render_template("tuchuang/upload.html")
    
@bp.route('/download/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    
    
