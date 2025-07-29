from flask import Blueprint

user_bp = Blueprint(
    "user",                # blueprint *name* (used for url_for)
    __name__,              # current module import name
    url_prefix="/user",    # prepended to every route in this bp
    template_folder="templates",
    static_folder="static",
)

from . import routes      # noqa: E402 (import after bp created)
