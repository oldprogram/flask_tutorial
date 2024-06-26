## V2.0

实现 http://127.0.0.1:5000/tuchuang 

- 一个 bakend 后台页面（找一个 moban6764.rar 的 Html 模板）
- 编写一个支持翻页的图片浏览页面（list，带翻页）（涉及大量 jinja 知识）
- 编写一个支持批量图片上传的页面（涉及一个典型的 js 知识）

注意：python 版本需要大于等于 3.9

</br>

upload 页面：

![][p1]

</br>

list 页面：

![][p2]

</br>

## V2.1

- 1.新增 share 页面：
	- 支持将文件上传、下载、删除，利用 css,js 主要是 js 技术
- 1.优化细节：
	- 支持中文名字文件上传（转为拼音）
	- icon 找到出处，换为标准 icon
	- 支持二维码生成
	- 支持根据主题生成不同的二维码
- 实现账户管理：
	- 每个人有独立的文件夹存储自己的 upload 图片
	- 支持头像自动随机生成（存储在每个用户的文件夹下的 my_avatar.svg ）

</br>

![][p3]

</br>

## V2.2

- 调整 API，总共分为：

	api | 描述 | 参数
	---|---|---
	`/user` | 用户私有资源页面 | 
	`/user/download/<name>` | 用户下载 | GET `?path=\xx\xxxx.png`
	`/user/view/page=<page>` | 用户资源列表 |
	`/tuchuang` | 公共图床页面 | 
	`/tuchuang/download/` | 图床资源下载 |
	`/tuchuang/view/page=<page>` | 图床资源列表 |
	`/share` | 公共共享页面 | POST file
	`/share/download/<name>` | 共享资源下载 |
	`/share/delete/<name>` | 共享资源删除 |
- 文件夹调整为：
	- private 存放各个用户私有文件
	- share/common 存放共享资源
	- share/tuchuang 存放图床资源

</br>

## V2.3

- 根据蓝图设计独立的文件夹，因此有目录结构的调整

	![][p4]

每个大块负责一个独立业务，每个里面有其独立的 MVC 结构。

</br>

## V2.4

- 增加 pcb 商城第一版（server_pcb）
    - chatgpt 一个类似淘宝商品页面，分离其 css 单独放置，将每个 product 的静态资源放在 view/pcb_static/products 中
    - 采用 jinja 比较简单
- 支持邮箱验证
    - M flaskr/server_auth/presenter/auth.py 
        - 利用 flask_mail 实现邮件发送功能（需要根据其中的 LINK1 配置 app.config，然后给 mail 初始化，具体遇到两个问题，看 link1 后面俩链接）
        - 对于获取验证码的接口由于会频繁发送邮件，因此利用 session（存储在浏览器端的 k-v），记录请求间隔和请求次数，进行限制）
    - M flaskr/server_auth/view/register.html （调整支持密码长度限制，用户邮箱检测，动态更改获取验证码状态，获取验证码）
    - flaskr/server_auth/view/verify.html  （用于给用户发送的邮件格式）

</br>



[p1]:./doc/pic/tuchuang_upload.png
[p2]:./doc/pic/tuchuang_list.png
[p3]:./doc/pic/tuchuang_share.png
[p4]:./doc/pic/tuchuang_dir_change.png
