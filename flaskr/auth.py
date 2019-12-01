import functools
import json
import requests
from flask import (Blueprint,
                   flash,
                   g,
                   redirect,
                   render_template,
                   request,
                   session,
                   url_for,
                   )
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import BASE_URL


bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View декоратор, который анонимного пользователя
       переводин на страницу регистрации """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """Если id пользователя сохранен в сессии,
       загрузить из базы данные об этом пользователе
       и сохранить их в переменной  ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        url_req = BASE_URL + "author/" + str(user_id)
        req = requests.get(url_req)
        user = req.json()
        if user["author_id"] == "Not_Found":
            g.user = None
        else:
            g.user = user


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Регистрация нового пользователся с проверкой на существование
    такого имени в базе. Запись имени и хешированного пароля в базу
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None

        url_req = BASE_URL + "author/" + username
        req = requests.get(url_req)

        if req.status_code == 200:
            user = req.json()
            if user["username"] == "Not_Found":
                error = None
            else:
                error = "User {0} is already registered.".format(username)

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        if error is None:
            password_hash = generate_password_hash(password)
            url_req = BASE_URL + "author/"
            headers = {'content-type': 'application/json'}
            data_user = {"username": username, "password_hash": password_hash}
            req = requests.post(url_req, data=json.dumps(data_user), headers=headers)
            if req.status_code == 200:
                message = "You registered as {0}. You may login and create, " \
                      "edit and delete your post!".format(username)
                flash(message)
                return redirect(url_for("auth.login"))
            else:
                error = "Not registered author {0} -- ".format(username) + str(req.status_code)
                flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Вход пользователя с добавлением его id
       в сессию с очисткой предыдущих ее параметров"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None
        user = None

        url_req = BASE_URL + "author/" + username
        req = requests.get(url_req)

        if req.status_code == 200:
            user = req.json()
            if user["username"] == "Not_Found":
                user = None

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Очистка текущей сессии"""
    session.clear()
    return redirect(url_for("index"))
