from flask import Blueprint

auth_bp = Blueprint(
    "auth",                # blueprint *name* (used for url_for)
    __name__,              # current module import name
    url_prefix="/auth",    # prepended to every route in this bp
    template_folder="templates",
    static_folder="static",
)

# print("printing from auth/__init__")
from . import routes      # noqa: E402 (import after bp created)
