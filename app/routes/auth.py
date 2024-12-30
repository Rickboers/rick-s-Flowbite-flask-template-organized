from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, bcrypt, oauth, limiter
from ..models import User
from ..utils import (
    redirect_if_authenticated,
    generate_reset_token,
    confirm_reset_token,
    send_reset_email,
)
from ..forms import LoginForm, RegistrationForm
import secrets

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
@redirect_if_authenticated
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(email=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("registration.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("15 per minute")
@redirect_if_authenticated
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.app1"))
    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/login/google")
@redirect_if_authenticated
def google_login():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    redirect_uri = url_for("auth.authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri, state=state)


@bp.route("/authorize")
@redirect_if_authenticated
def authorize():
    if request.args.get("state") != session.pop("oauth_state", None):
        return "State mismatch. Possible CSRF attack.", 400
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.userinfo()
    user = User.query.filter_by(email=user_info["email"]).first()
    if not user:
        user = User(email=user_info["email"])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for("main.app1"))


@bp.route("/reset_password", methods=["GET", "POST"])
@redirect_if_authenticated
def reset_request():
    if request.method == "POST":
        email = request.form["email"]
        token = generate_reset_token(email)
        reset_url = url_for("auth.reset_token", token=token, _external=True)
        send_reset_email(email, reset_url)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("auth.login"))
    return render_template("reset_request.html")


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
@redirect_if_authenticated
def reset_token(token):
    email = confirm_reset_token(token)
    if not email:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("auth.reset_request"))

    if request.method == "POST":
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = hashed_password
            db.session.commit()
            flash("Your password has been updated!", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found.", "danger")
            return redirect(url_for("auth.reset_request"))

    return render_template("reset_token.html")
