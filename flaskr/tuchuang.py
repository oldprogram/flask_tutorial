#!/usr/bin/env python
# coding=utf-8

import os
import random
import time
import datetime
import python_avatars as pa
from flask import g
from datetime import datetime
from flask import Blueprint
from flask import Flask, flash, request, redirect, url_for, jsonify
from flask import send_from_directory
from flask import render_template
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = basedir+'/static/file/img'
SHARE_FOLDER = basedir+'/static/file/share'
ALLOWED_IMG_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_SHARE_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'py', 'c'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SHARE_FOLDER'] = SHARE_FOLDER

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("tuchuang", __name__, url_prefix="/tuchuang")

#####################################################################################
class File:
    def __init__(self, file_path,prefix):
        self.path = file_path
        self.url  = self.path.removeprefix(prefix)
        self.name = os.path.basename(file_path)
        self.size = os.path.getsize(file_path)
        self.kind = self.name.rsplit('.', 1)[1].lower() 
        self.date = time.strftime("%Y-%m-%d %H:%M:%S",
                    time.localtime(os.path.getmtime(file_path)))

    def info_to_json(self):
        return {'name':self.name,'size':self.size,'kind':self.kind,'date':self.date, 'url':self.url}
    
    @staticmethod
    def search(path):
        file_list = []
        prefix = path
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                img = File(file_path,prefix)
                file_list.append(img)
        file_list.sort(key=lambda x: x.date, reverse=True)

        return file_list
    
    @staticmethod
    def allowed_file(filename,kind):
        if kind == 'img':
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXTENSIONS
        elif kind == 'share':
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_SHARE_EXTENSIONS

    @staticmethod  
    def is_chinese(string):
        """
        https://blog.csdn.net/gixome/article/details/123249482
        检查整个字符串是否包含中文
        :param string: 需要检查的字符串
        :return: bool
        """
        for ch in string:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
    
        return False
    
    @staticmethod  
    def to_pinyin(filename):
        name = filename.split('.')[0]
        ext = filename.split('.')[1]
        filename = '_'.join(lazy_pinyin(name)) + '.' + ext
        return filename


#####################################################################################
@bp.route('/upload', methods=['GET', 'POST'])
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
        if file and File.allowed_file(file.filename,'img'):
            # 获取安全的文件名 正常文件名
            # 支持中文，转换为拼音
            if File.is_chinese(file.filename):
                file.filename = File.to_pinyin(file.filename)
            filename = secure_filename(file.filename)
            
            # 生成随机数
            random_num = random.randint(0, 100)
            # f.filename.rsplit('.', 1)[1] 获取文件的后缀
            # filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random_num) + "." + filename.rsplit('.', 1)[1]
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + filename
            file_path = app.config['UPLOAD_FOLDER'] + '/' + secure_filename(g.user["username"])   # basedir 代表获取当前位置的绝对路径
            
            # 如果文件夹不存在，就创建文件夹
            if not os.path.exists(file_path):
	            os.makedirs(file_path)

            print(secure_filename(g.user["username"]))

            file.save(os.path.join(file_path, filename))
            return redirect(url_for('tuchuang.download_file', name=filename))
    return render_template("tuchuang/upload.html")
    
@bp.route('/share', methods=['GET', 'POST'])
@login_required
def share_file():
    if request.method == 'POST':
        num_files = len(os.listdir(app.config['SHARE_FOLDER']))
        if num_files >= 10:
            flash('Share file limit 10')
            return jsonify(state="fail",reason="share file limit 10")
        
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
        if file and File.allowed_file(file.filename,'share'):
            # 获取安全的文件名 正常文件名
            # 支持中文，转换为拼音
            if File.is_chinese(file.filename):
                file.filename = File.to_pinyin(file.filename)
            filename = secure_filename(file.filename)

            # 生成随机数
            random_num = random.randint(0, 100)
            # f.filename.rsplit('.', 1)[1] 获取文件的后缀
            # filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random_num) + "." + filename.rsplit('.', 1)[1]
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + filename
            file_path = app.config['SHARE_FOLDER']    # basedir 代表获取当前位置的绝对路径
            
            # 如果文件夹不存在，就创建文件夹
            if not os.path.exists(file_path):
	            os.makedirs(file_path)
	
            file.save(os.path.join(file_path, filename))
            
            file_info = File(os.path.join(file_path, filename),file_path).info_to_json()
            file_info['state'] = 'success'
 
            return jsonify(file_info)
        else:
            return jsonify(state="fail",reason="file kind not allowed")
        
    files = File.search(app.config['SHARE_FOLDER'])
    return render_template("tuchuang/share.html",my_files=files)

@bp.route('/download/<name>')
@login_required
def download_file(name):
    file_path = app.config["UPLOAD_FOLDER"] + '/' + secure_filename(g.user["username"]) 
    # 如果没有头像图片，则自动生成一个
    # https://pypi.org/project/python-avatars/
    if name == 'my_avatar.svg':
        avatar_path = file_path + '/my_avatar.svg'
        if not os.path.exists(avatar_path):
            if not os.path.exists(file_path):
	            os.makedirs(file_path)
            pa.Avatar.random().render(avatar_path)

    return send_from_directory(file_path, name)
    
@bp.route('/download_share/<name>')
def download_share_file(name):
    return send_from_directory(app.config["SHARE_FOLDER"], name)

@bp.route('/delete_share/<name>')
@login_required
def delete_share_file(name):
    # https://blog.csdn.net/weixin_43215588/article/details/121189959
    # Flask——返回json数据的方法
    name = os.path.basename(name)
    file = app.config["SHARE_FOLDER"]+'/'+name
    if os.path.exists(file):
        os.remove(file)
    
    return jsonify(state="success")

@bp.route('/view/page=<page>')
@login_required
def view(page):
    print(os.getcwd()) # 输出当前工作目录的路径
    print(os.path.abspath('.')) # 输出当前文件所在目录的绝对路径

    imgs = File.search(app.config['UPLOAD_FOLDER']+ '/' + secure_filename(g.user["username"]))
    total_num = len(imgs)
    step = 10
    index_start = int(page) * step
    index_end = int(page) * step + step
    if index_end > total_num:
        index_end = total_num

    return render_template('tuchuang/view.html', 
            img_start = index_start, 
            img_end = index_end,
            img_step = step,
            img_num = total_num ,
            my_imgs=imgs[index_start:index_end])

@bp.route('/')
@login_required
def main():
    return render_template('tuchuang/backend.html')
   
