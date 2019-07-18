from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required

from flaskr.db import list_tp_to_list_dict, tp_to_dict, get_conn_db, BASE_URL

import requests
import json

bp = Blueprint('blog', __name__)


@bp.route("/")
def index():
    url_req = BASE_URL + "posts/"
    req = requests.get(url_req)
    lst_bd = req.json()
    return render_template("blog/index.html", posts=lst_bd)


def get_post(post_id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param post_id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
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
    """Create a new post for the current user."""
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


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            url_req = BASE_URL + "posts/" + str(id)
            headers = {'content-type': 'application/json'}
            data_post = {"title": title, "body": body, "id": id}

            req = requests.put(url_req, data=json.dumps(data_post), headers=headers)
            if req.status_code == 200:
                message = "You update your post!"
                flash(message)
            else:
                error = "Not updated post -- " + str(req.status_code)
                flash(error)

            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM post WHERE id = %s", (id,)
    )
    cur.close()
    conn.commit()
    conn.close()
    return redirect(url_for("blog.index"))
