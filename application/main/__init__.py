from flask import Blueprint

main_bp = Blueprint(
    "main",                        # blueprint *name* (used for url_for)
    __name__,                       # current module import name
    url_prefix="",                  # prepended to every route in this bp
    template_folder="templates",
    static_folder="static",
    static_url_path="/main/static"
)

# print("printing from main/__init__")
from . import routes      # noqa: E402 (import after bp created)
