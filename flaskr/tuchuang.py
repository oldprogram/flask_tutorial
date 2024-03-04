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
PRIVATE_FOLDER = basedir+'/static/file/private'
SHARE_COMMON_FOLDER = basedir+'/static/file/share/common'
SHARE_TUCHUANG_FOLDER = basedir+'/static/file/share/tuchuang'
ALLOWED_IMG_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_SHARE_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'py', 'c'}

app = Flask(__name__)
app.config['PRIVATE_FOLDER'] = PRIVATE_FOLDER
app.config['SHARE_COMMON_FOLDER'] = SHARE_COMMON_FOLDER
app.config['SHARE_TUCHUANG_FOLDER'] = SHARE_TUCHUANG_FOLDER

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
        
        tmp = self.name.rsplit('.', 1)
        if len(tmp) < 2:
            self.kind = 'null'
        else:
            self.kind = tmp[1].lower() 

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
    
    @staticmethod  
    def simplify_path(path: str) -> str:
        f_lst_new = []

        for i in path.split('/'):
            if i == '' or i == '.':
                pass
            elif i == '..':
                if f_lst_new != []:
                    f_lst_new.pop()
            else:
                f_lst_new.append(i)
        return '/' + '/'.join(f_lst_new)
        # 原文链接：https://blog.csdn.net/qq_35164554/article/details/122342584


##############################################################################
# upload & view (private) 
##############################################################################
@bp.route('/user', methods=['GET', 'POST'])
@login_required
def user_upload_file():
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
            file_path = app.config['PRIVATE_FOLDER'] + '/' + secure_filename(g.user["username"])   # basedir 代表获取当前位置的绝对路径
            
            # 如果文件夹不存在，就创建文件夹
            if not os.path.exists(file_path):
	            os.makedirs(file_path)

            print(secure_filename(g.user["username"]))

            file.save(os.path.join(file_path, filename))
            return redirect(url_for('tuchuang.download_file', name=filename))
    return render_template("tuchuang/upload.html")

@bp.route('/user/download/<name>')
@login_required
def user_download_file(name):
    file_path = app.config["PRIVATE_FOLDER"] + '/' + secure_filename(g.user["username"]) 
    # 如果没有头像图片，则自动生成一个
    # https://pypi.org/project/python-avatars/
    if name == 'my_avatar.svg':
        avatar_path = file_path + '/my_avatar.svg'
        if not os.path.exists(avatar_path):
            if not os.path.exists(file_path):
	            os.makedirs(file_path)
            pa.Avatar.random().render(avatar_path)

    return send_from_directory(file_path, name)
    
@bp.route('/user/view/page=<page>')
@login_required
def user_view(page):
    print(os.getcwd()) # 输出当前工作目录的路径
    print(os.path.abspath('.')) # 输出当前文件所在目录的绝对路径

    imgs = File.search(app.config['PRIVATE_FOLDER']+ '/' + secure_filename(g.user["username"]))
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

##############################################################################
# tuchuang
##############################################################################
@bp.route('/tuchuang', methods=['GET', 'POST'])
@login_required
def tuchuang():
    return render_template("tuchuang/tuchuang.html")

@bp.route('/tuchuang/download/', methods=['GET'])
def tuchuang_download_file():
    # 判断请求接口是否带参数，否则加上自定义字符串（没有这个文件夹，返回404）
    args = request.args.get('path') or 'no_file'
    args = File.simplify_path(args)
    # 拼接文件地址
    file_path = app.config['SHARE_TUCHUANG_FOLDER'] + os.path.dirname(args)
    name = os.path.basename(args)
    #print('args->',args)
    #print('file_path->',file_path)
    #print('name->',name)

    return send_from_directory(file_path, name)

@bp.route('/tuchuang/view/page=<page>')
@login_required
def tuchuang_view(page):
    print(os.getcwd()) # 输出当前工作目录的路径
    print(os.path.abspath('.')) # 输出当前文件所在目录的绝对路径

    imgs = File.search(app.config['SHARE_TUCHUANG_FOLDER'])
    total_num = len(imgs)
    step = 10
    index_start = int(page) * step
    index_end = int(page) * step + step
    if index_end > total_num:
        index_end = total_num

    return render_template('tuchuang/tuchuang.html', 
            img_start = index_start, 
            img_end = index_end,
            img_step = step,
            img_num = total_num ,
            my_imgs=imgs[index_start:index_end])


##############################################################################
# share 
##############################################################################
@bp.route('/share', methods=['GET', 'POST'])
@login_required
def share_file():
    if request.method == 'POST':
        num_files = len(os.listdir(app.config['SHARE_COMMON_FOLDER']))
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
            file_path = app.config['SHARE_COMMON_FOLDER']    # basedir 代表获取当前位置的绝对路径
            
            # 如果文件夹不存在，就创建文件夹
            if not os.path.exists(file_path):
	            os.makedirs(file_path)
	
            file.save(os.path.join(file_path, filename))
            
            file_info = File(os.path.join(file_path, filename),file_path).info_to_json()
            file_info['state'] = 'success'
 
            return jsonify(file_info)
        else:
            return jsonify(state="fail",reason="file kind not allowed")
        
    files = File.search(app.config['SHARE_COMMON_FOLDER'])
    return render_template("tuchuang/share.html",my_files=files)

@bp.route('/share/download/<name>')
def share_download_file(name):
    return send_from_directory(app.config["SHARE_COMMON_FOLDER"], name)

@bp.route('/share/delete/<name>')
@login_required
def share_delete_file(name):
    # https://blog.csdn.net/weixin_43215588/article/details/121189959
    # Flask——返回json数据的方法
    name = os.path.basename(name)
    file = app.config["SHARE_COMMON_FOLDER"]+'/'+name
    if os.path.exists(file):
        os.remove(file)
    
    return jsonify(state="success")

##############################################################################
# root
##############################################################################
@bp.route('/')
@login_required
def main():
    return render_template('tuchuang/backend.html')
   
