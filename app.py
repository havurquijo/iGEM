from pathlib import Path
import os
import json
import urllib.request
import urllib.error
from typing import Tuple, List, Dict
from flask import Flask, render_template, abort, url_for
from flask_frozen import Freezer

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "wiki"
PAGES = TEMPLATES / "pages"
STATIC = BASE / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATES),
    static_folder=str(STATIC),
    static_url_path="/static",
)

app.config.update(
    # Allow overriding destination via env var so the repo can use `docs/` for GitHub Pages
    FREEZER_DESTINATION=os.environ.get("FREEZER_DESTINATION", str(BASE / "public")),
    FREEZER_RELATIVE_URLS=True,
    FREEZER_REMOVE_EXTRA_FILES=True,
    FREEZER_IGNORE_MIMETYPE_WARNINGS=True,
    FREEZER_IGNORE_404_NOT_FOUND=False,
)

freezer = Freezer(app)

@app.route("/")
def home():
    # sua home continua como public/index.html
    return render_template("pages/home.html")



# Também expor explicitamente /index.html para garantir que o freezer gere um arquivo
# index.html (útil para deploy em GitHub Pages que espera index.html na raiz)
@app.route("/index.html")
def index_html():
    return home()


# Explicit routes for team members to ensure local runs render the page with
# JSON-provided team data.
@app.route("/team/members.html")
def team_members_html():
    team_members, advisors = _load_members_json()
    return render_template("pages/team/members.html", team_members=team_members, advisors=advisors)


@app.route("/team/members")
def team_members_noext():
    return team_members_html()

def _render_page(page: str):
    page = page.strip("/")
    f1 = PAGES / f"{page}.html"
    if f1.is_file():
        # ex.: pages/team/members.html
        # Special-case: load members JSON and pass into template when rendering the
        # team members page so the members list can come from JSON (remote with
        # local fallback).
        if page == "team/members":
            team_members, advisors = _load_members_json()
            return render_template(f"pages/{page}.html", team_members=team_members, advisors=advisors)
        return render_template(f"pages/{page}.html")
    f2 = PAGES / page / "index.html"
    if f2.is_file():
        # ex.: pages/team/members/index.html
        rel = f2.relative_to(TEMPLATES).as_posix()
        if rel == "pages/team/members/index.html":
            team_members, advisors = _load_members_json()
            return render_template(rel, team_members=team_members, advisors=advisors)
        return render_template(rel)
    return abort(404)


def _load_members_json() -> Tuple[List[Dict], List[Dict]]:
    """Load members JSON from the remote IGEM static URL, fallback to
    local `static/members.json` if anything goes wrong.

    Returns two lists of dicts: (team_members, advisors). Each dict will have
    the shape expected by the `member_card.html` include: `image`, `name`,
    `description` (HTML string).
    """
    remote_url = "https://static.igem.wiki/teams/5560/members/members.json"
    local_path = STATIC / "members.json"

    data = None
    # Try remote fetch first
    try:
        with urllib.request.urlopen(remote_url, timeout=5) as resp:
            raw = resp.read()
            data = json.loads(raw)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, Exception):
        # fallback to local file
        try:
            with open(local_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = []

    team_members: List[Dict] = []
    advisors: List[Dict] = []

    for item in data:
        name = item.get("name", "")
        course = item.get("course", "")
        level = item.get("level", "")
        role = item.get("role_in_team", "")
        committees = item.get("committees", []) or []

        # Use the image field from JSON directly
        image = item.get("image", "")
        
        # Description as HTML (level + course + committees)
        parts = []
        if level:
            parts.append(level)
        if course:
            parts.append(course)
        if committees:
            parts.append("Committees: " + ", ".join(committees))
        description = "<br>".join(parts)

        member = {"image": image or "", "name": name, "description": description}

        # Consider advisors/principal investigators as advisors list
        role_l = role.lower() if isinstance(role, str) else ""
        if "advisor" in role_l or "principal" in role_l or "professor" in role_l:
            advisors.append(member)
        else:
            team_members.append(member)

    return team_members, advisors

# === URLs CANÔNICAS SEM '/' NO FIM: /slug.html ===
@app.route("/<path:page>.html", endpoint="pages")
def pages_route_html(page: str):
    return _render_page(page)

# Compat local (não usada pelo freezer): aceitar /slug (sem .html)
@app.route("/<path:page>", endpoint="pages_extless")
def pages_route_extless(page: str):
    return _render_page(page)

# Helper global: sempre emitir .html (sem barra final)
@app.template_global()
def page_url(page: str) -> str:
    return url_for("pages", page=page)

# Generator do freezer apontando para o endpoint 'pages'
@freezer.register_generator
def pages():
    for f in PAGES.rglob("*.html"):
        rel = f.relative_to(PAGES).as_posix()  # ex.: team/members/index.html
        if rel == "home.html":
            continue
        if rel.endswith("/index.html"):
            slug = rel[: -len("/index.html")]   # team/members -> /team/members.html
        else:
            slug = rel[: -5]                    # docs/intro.html -> /docs/intro.html
        yield {"page": slug}

# Also register the same generator for the extless endpoint so the freezer
# can produce URLs for `/...` (without .html). This prevents the
# MissingURLGeneratorWarning during `freeze`.
@freezer.register_generator
def pages_extless():
    for item in pages():
        yield item

# Verificação rápida antes do freeze
@app.cli.command("verify")
def verify_cmd():
    errors = 0
    with app.test_client() as c:
        for f in PAGES.rglob("*.html"):
            rel = f.relative_to(PAGES).as_posix()
            if rel == "home.html":
                continue
            slug = rel[:-len("/index.html")] if rel.endswith("/index.html") else rel[:-5]
            r = c.get(f"/{slug}.html")
            if r.status_code != 200:
                print(f"[FAIL] /{slug}.html -> {r.status_code}")
                errors += 1
    print(f"[verify] Erros: {errors}")

@app.cli.command("freeze")
def freeze_cmd():
    freezer.freeze()

if __name__ == "__main__":
    app.run(port=8080)
