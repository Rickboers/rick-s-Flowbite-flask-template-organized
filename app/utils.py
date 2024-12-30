from flask import redirect, url_for
from flask_login import current_user
from functools import wraps
from itsdangerous import URLSafeTimedSerializer
import requests
from . import db


def redirect_if_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function

