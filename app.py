# app.py
# Combine main.py, admin.py, staff.py into one WSGI app for freezing or serving.
# Usage with Frozen-Flask:
#   from app import app   # your freeze.py should import this

from typing import Callable, Iterable
from werkzeug.wrappers import Response
from flask import Flask

# --- Import your three existing Flask apps ---
# Each of these files must define `app = Flask(__name__, ...)`
# Adjust names/paths if your modules are in a package (e.g., from src.main import app as main_app)
from main import app as main_app
from admin import app as admin_app
from staff import app as staff_app


class Cascade:
    """
    WSGI middleware that tries multiple apps in order until one returns
    a non-404 response. Perfect when route paths are unique across apps.
    """

    def __init__(self, apps: Iterable[Callable]):
        self.apps = list(apps)

    def __call__(self, environ, start_response):
        # Try each subapp; if 404, fall through to the next.
        for i, subapp in enumerate(self.apps):
            status_holder = {}

            def _sr(status: str, headers: list, exc_info=None):
                status_holder["status"] = status
                status_holder["headers"] = headers
                status_holder["exc_info"] = exc_info
                return start_response(status, headers, exc_info)

            result = subapp(environ, _sr)

            # If this subapp didn't return 404, use it.
            status = status_holder.get("status", "500 INTERNAL SERVER ERROR")
            if not status.startswith("404"):
                return result

            # If 404, we must fully consume/close the iterable before trying next app.
            try:
                # Some WSGI apps return iterables; exhaust/close them politely.
                if hasattr(result, "__iter__"):
                    for _ in result:
                        pass
            finally:
                if hasattr(result, "close"):
                    result.close()

        # If none handled it, return a 404 from a minimal Response
        res = Response(
            "Not Found", status=404, content_type="text/plain; charset=utf-8"
        )
        return res(environ, start_response)


# This minimal Flask app exists to provide a single `app` object that
# your freezer (and dev server) can use, while delegating handling to the cascade.
app = Flask(__name__)


# Delegate *all* actual handling to the cascade of your three apps.
# Order matters: first match wins. Since you said routes are unique, any order is fine.
app.wsgi_app = Cascade([main_app, admin_app, staff_app])  # type: ignore[attr-defined]


# Optional: helper to enumerate all unique, no-parameter GET paths across apps.
# You can import and use this inside your freeze.py if you want explicit freezing.
def all_get_paths() -> list:
    def collect(flask_app):
        out = []
        for rule in flask_app.url_map.iter_rules():
            if (
                "GET" in rule.methods
                and not rule.arguments
                and not rule.rule.startswith("/static")
            ):
                out.append(rule.rule)
        return out

    # Use a set to deduplicate across apps
    paths = set(collect(main_app)) | set(collect(admin_app)) | set(collect(staff_app))
    # Ensure root is first for friendliness
    return ["/"] + sorted(p for p in paths if p != "/")


if __name__ == "__main__":
    # Local dev server for sanity checks
    # Visit /__routes to see the combined GET routes discovered from all three apps.
    app.run(host="0.0.0.0", port=5000, debug=True)
