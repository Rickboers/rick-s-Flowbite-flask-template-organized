from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html")


@bp.route("/app")
@login_required
def app1():
    user_id = current_user.id
    return render_template("app.html", user_id=user_id)
