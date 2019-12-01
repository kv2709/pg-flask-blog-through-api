from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import BASE_URL

import requests
import json

bp = Blueprint('blog', __name__)


@bp.route("/")
def index():
    """
    Звпрос к API по url "posts/" и получение из базы всех постов
    :return: передача содержимого всех постов в шаблон blog/index.html
    """
    url_req = BASE_URL + "posts/"
    req = requests.get(url_req)
    lst_bd = req.json()
    return render_template("blog/index.html", posts=lst_bd)


def get_post(post_id, check_author=True):
    """
    Отдает все посты и их авторов по id
    check_author проверяет что данный id существует
    и опционально, что текущий пользователь user является автором author.

    :param post_id: id поста для get запроса
    :param check_author: требование проверки текущего пользователя на авторство
    :return: содержание поста с информаий об авторе
    :raise 404: если посто с таким id не существует
    :raise 403: если текущимй пользователь не является автором
    """

    url_req = BASE_URL + "posts/" + str(post_id)
    req = requests.get(url_req)
    post = req.json()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Создает новый пост текущего поьзлователя"""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            url_req = BASE_URL + "posts/"
            headers = {'content-type': 'application/json'}
            data_user = {"title": title, "body": body, "author_id": g.user["id"]}
            req = requests.post(url_req, data=json.dumps(data_user), headers=headers)
            if req.status_code == 200:
                message = "You created new post!"
                flash(message)
            else:
                error = "Not created post -- " + str(req.status_code)
                flash(error)
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:post_id>/update", methods=("GET", "POST"))
@login_required
def update(post_id):
    """Обновляет в базе отредактированный автором пост"""
    post = get_post(post_id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            url_req = BASE_URL + "posts/" + str(post_id)
            headers = {'content-type': 'application/json'}
            data_post = {"title": title, "body": body, "id": post_id}

            req = requests.put(url_req, data=json.dumps(data_post), headers=headers)
            if req.status_code == 200:
                message = "You update your post!"
                flash(message)
            else:
                error = "Not updated post -- " + str(req.status_code)
                flash(error)

            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:post_id>/delete", methods=("POST",))
@login_required
def delete(post_id):
    """Удаляет пост, гарантируя, что сообщение существует
       и что зарегистрированный пользователь является автор поста
    """
    url_req = BASE_URL + "posts/" + str(post_id)
    req = requests.delete(url_req)
    if req.status_code == 200:
        message = "You deleted your post!"
        flash(message)
    else:
        error = "Not deleted post -- " + str(req.status_code)
        flash(error)

    return redirect(url_for("blog.index"))
