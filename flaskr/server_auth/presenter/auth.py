import functools

from flask import Blueprint
from flask import Flask
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import jsonify
from flask_mail import Mail, Message
from datetime import datetime, timedelta, timezone
import random
import string

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth",template_folder="../view")

######################################################################
# 邮件确认相关函数
app = Flask(__name__)
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)  # 设置 session 的过期时间
app.config['SECRET_KEY'] = 'abcdefghigklmn'  
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '953521476@qq.com'
app.config['MAIL_PASSWORD'] = 'abcdefghigklmn'
app.config['MAIL_DEFAULT_SENDER'] = ('BTFZ', '953521476@qq.com')

mail = Mail(app)

# Define constants for limiting requests
REQUEST_INTERVAL = 60  # 1 minutes interval
MAX_REQUESTS_PER_EMAIL = 3  # Maximum requests allowed per email

def generate_random_code(length=6):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def send_email(to_email, subject, template):
    msg = Message(
        subject,
        recipients=[to_email],
        html=template,
        sender=app.config['MAIL_USERNAME']
    )
    
    # LINK1:https://wx.mail.qq.com/list/readtemplate?name=app_intro.html#/agreement/authorizationCode
    # https://stackoverflow.com/questions/28466384/python-flask-email-keyerror-keyerror-mail
    # https://stackoverflow.com/questions/65997108/flask-mail-ssl-wrong-version-number-wrong-version-number-ssl-c1123
    mail.send(msg)

######################################################################

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )

@bp.route("/get_mail_check_code", methods=("GET", "POST"))
def get_mail_check_code():
    if request.method == 'POST':
        email = request.form['email']

        # Get last request time from session (这里不存具体时间，会丢掉时区，从而要做很多转换）
        # https://stackoverflow.com/questions/71995767/python-datetime-utcnow-does-not-set-timezone
        last_request_time = session.get(f'{email}_last_request_time')
        now_timestamp = datetime.now().timestamp()
        #print(session)
        if last_request_time and (now_timestamp-last_request_time < REQUEST_INTERVAL):
            #print(last_request_time, now_timestamp, now_timestamp-last_request_time)
            return jsonify(state="fail", reason="too frequent requests")

        # Check if this email has reached the maximum number of requests
        request_count = session.get(f'{email}_request_count', 0)
        if request_count >= MAX_REQUESTS_PER_EMAIL:
            return jsonify(state="fail", reason="maximum requests reached")

        # Generate verification code and send email
        verification_code = generate_random_code()
        session[f'{email}_verification_code'] = verification_code
        session[f'{email}_last_request_time'] = datetime.now().timestamp()
        session[f'{email}_request_count'] = request_count + 1

        html = render_template("verify.html", verification_code=verification_code, email=email)
        send_email(email, 'BTFZ 网站验证码', html)

        return jsonify(state="success")

    return jsonify(state="fail", reason="bad request")

@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        checkcode = request.form["checkcode"]

        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif not checkcode:
            error = "CheckCode is required."
        else:
            verification_code = session.get(f'{username}_verification_code')
            last_request_time = session.get(f'{username}_last_request_time')
            print(verification_code,last_request_time)
            if not (verification_code != None and verification_code == checkcode 
                and last_request_time != None and datetime.now().timestamp() - last_request_time <= REQUEST_INTERVAL*2):
                error = "CheckCode is error or timeout."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("main.index"))

        flash(error)

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("main.index"))
