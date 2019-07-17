import functools

from flask import (
    Blueprint,
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

import json
import requests

bp = Blueprint("auth", __name__, url_prefix="/auth")


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
        url_req = BASE_URL + "author/" + str(user_id)
        req = requests.get(url_req)
        g.user = req.json()
        print("load_logged_in_user")


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None
        user = None

        url_req = BASE_URL + "author/" + username
        req = requests.get(url_req)
        # Подумать над логикой обработки исключений
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
    """Log in a registered user by adding the user id to the session."""
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
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
