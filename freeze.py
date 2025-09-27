# freeze.py
# Auto-discover (crawl) pages—including dynamic URLs already linked in your app—
# and freeze them to /build for static hosting (e.g., Netlify).
#
# Requirements (add to requirements.txt):
#   frozen-flask
#   beautifulsoup4
#
# Run locally:
#   python freeze.py
#
# Netlify:
#   Build command: python freeze.py
#   Publish directory: build

import os
import re
from urllib.parse import urlparse, urlunparse, urljoin, urlencode, parse_qsl

from flask_frozen import Freezer
from bs4 import BeautifulSoup

# Import your Flask app (main site lives in main.py)
from main import app  # noqa: F401

# --------------------------- Freezer config -----------------------------------
app.config.setdefault("FREEZER_DESTINATION", os.path.join(os.getcwd(), "build"))
app.config.setdefault("FREEZER_RELATIVE_URLS", True)
# Optional: set a base URL if your templates use absolute URLs
# app.config["FREEZER_BASE_URL"] = "https://your-site.netlify.app/"

freezer = Freezer(app)

# --------------------------- Helpers ------------------------------------------
INTERNAL_SCHEMES = {"", "http", "https"}
HTML_CT = ("text/html", "text/html; charset=utf-8")

# Limit the crawl to avoid infinite spaces:
MAX_PAGES = 5000  # total unique pages
MAX_DEPTH = 20  # BFS depth
MAX_QUERY_PAGES = 30  # cap for expanding ?page=, ?p=, etc.

# Query keys we’re willing to keep/follow (prevents combinatorial explosions)
WHITELISTED_QUERY_KEYS = {"page", "p", "lang", "locale", "q"}

# Common “next” patterns
NEXT_TEXT_RE = re.compile(r"^\s*(next|more|older)\s*$", re.I)
REL_NEXT_VALS = {"next", "Next", "NEXT"}


def normalize_url(path_or_url: str) -> str:
    """
    Keep only path + query for internal URLs, drop fragments and scheme/host.
    Normalize multiple slashes and trailing slashes (except '/').
    """
    if not path_or_url:
        return ""
    u = urlparse(path_or_url)
    # Only internal links (no netloc)
    if u.netloc:
        return ""
    if u.scheme not in INTERNAL_SCHEMES:
        return ""

    path = re.sub(r"/{2,}", "/", u.path or "/")  # collapse //
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    # Whitelist query params to keep crawl sane
    if u.query:
        qs = [
            (k, v)
            for (k, v) in parse_qsl(u.query, keep_blank_values=True)
            if k in WHITELISTED_QUERY_KEYS
        ]
        query = urlencode(qs, doseq=True)
    else:
        query = ""

    normalized = urlunparse(
        ("", "", path or "/", "", query, "")
    )  # scheme, netloc empty; no fragment
    return normalized or "/"


def is_html_ok(resp) -> bool:
    if not resp:
        return False
    if resp.status_code != 200:
        return False
    ct = (resp.content_type or "").split(";")[0].strip()
    return ct in {"text/html", "application/xhtml+xml"}


def extract_internal_links(html_bytes: bytes) -> set:
    urls = set()
    try:
        soup = BeautifulSoup(html_bytes, "html.parser")
    except Exception:
        return urls

    # Anchor tags
    for a in soup.find_all("a", href=True):
        url = normalize_url(a["href"])
        if url and url.startswith("/"):
            urls.add(url)

    # <link rel="next"> etc.
    for link in soup.find_all("link", href=True):
        rel = link.get("rel") or []
        if any(r in REL_NEXT_VALS for r in rel):
            url = normalize_url(link["href"])
            if url and url.startswith("/"):
                urls.add(url)

    # Basic pagination autodiscovery: if there is a visible "Next" anchor
    for a in soup.find_all("a", href=True):
        if a.string and NEXT_TEXT_RE.match(a.string):
            url = normalize_url(a["href"])
            if url and url.startswith("/"):
                urls.add(url)

    return urls


def expand_query_pagination(url: str) -> list:
    """
    For URLs with ?page= or ?p=, generate additional pages up to MAX_QUERY_PAGES
    by incrementing the integer value. Stop if non-int or missing.
    """
    u = urlparse(url)
    qs = dict(parse_qsl(u.query, keep_blank_values=True))
    key = None
    for k in ("page", "p"):
        if k in qs:
            key = k
            break
    if not key:
        return [url]

    try:
        base_num = int(qs[key])
    except Exception:
        return [url]

    out = [url]  # include the original
    for i in range(base_num + 1, base_num + 1 + MAX_QUERY_PAGES):
        qs[key] = str(i)
        new_q = urlencode(list(qs.items()), doseq=True)
        out.append(urlunparse(("", "", u.path, "", new_q, "")))
    return out


# --------------------------- Generators ---------------------------------------
@freezer.register_generator
def crawl_site():
    """
    Breadth-first crawl starting from:
      - "/"
      - all simple GET routes (no params)
    Follow internal links and basic pagination (?page=?).
    Yield each discovered path so Frozen-Flask saves it.
    """
    client = app.test_client()

    # Seeds: home + simple static routes
    to_visit = set(["/"])
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and not rule.arguments:
            if not rule.rule.startswith("/static"):
                to_visit.add(normalize_url(rule.rule))

    seen = set()
    depth = {"/": 0}
    pages_frozen = 0

    while to_visit:
        path = to_visit.pop()
        if path in seen:
            continue
        seen.add(path)
        d = depth.get(path, 0)
        if d > MAX_DEPTH:
            continue

        resp = client.get(path)
        if not is_html_ok(resp):
            continue

        # Yield the current path to be frozen
        yield path
        pages_frozen += 1
        if pages_frozen >= MAX_PAGES:
            break

        # Extract and queue links
        new_links = extract_internal_links(resp.data)
        for url in new_links:
            # Expand pagination if present
            candidates = expand_query_pagination(url)
            for c in candidates:
                if c not in seen:
                    to_visit.add(c)
                    depth[c] = d + 1


# Example: If you later want to *force* enumeration for certain patterns
# (e.g., /item/<int:id>) without relying on links, you can add a generator:
#
# @freezer.register_generator
# def force_items_range():
#     for item_id in range(1, 501):  # adjust range
#         yield f"/item/{item_id}"


# --------------------------- Main --------------------------------------------
if __name__ == "__main__":
    os.makedirs(app.config["FREEZER_DESTINATION"], exist_ok=True)
    freezer.freeze()
    print(f"✅ Frozen site written to: {app.config['FREEZER_DESTINATION']}")
