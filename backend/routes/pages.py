from flask import Blueprint, send_from_directory, current_app
import os

pages_bp = Blueprint("pages", __name__)

# The Vue app is built by Vite into frontend/dist. Flask serves that build in
# production; during development the Vite dev server (npm run dev) proxies API
# calls to Flask instead.


def _dist_dir():
    return os.path.join(current_app.root_path, "..", "frontend", "dist")


def _spa_index():
    index_path = os.path.join(_dist_dir(), "index.html")
    if os.path.exists(index_path):
        return send_from_directory(_dist_dir(), "index.html")
    # Helpful message instead of a silent 404 when the SPA hasn't been built.
    return (
        "<h2>Frontend not built</h2>"
        "<p>Run <code>cd frontend &amp;&amp; npm install &amp;&amp; npm run build</code>, "
        "or use <code>npm run dev</code> for the Vite dev server.</p>",
        503,
    )


# Hashed JS/CSS assets produced by the Vite build.
@pages_bp.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(_dist_dir(), "assets"), filename)


# SPA routes — every client-side route returns the same index.html and lets
# Vue Router take over. Paths mirror the Vue Router config.
@pages_bp.route("/")
@pages_bp.route("/register")
@pages_bp.route("/admindashboard")
@pages_bp.route("/adminstaff")
@pages_bp.route("/admintreks")
@pages_bp.route("/adminusers")
@pages_bp.route("/adminbookings")
@pages_bp.route("/adminreports")
@pages_bp.route("/adminnotifications")
@pages_bp.route("/staffdashboard")
@pages_bp.route("/userdashboard")
def spa(**kwargs):
    return _spa_index()
