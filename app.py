from pathlib import Path
import os
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

def _render_page(page: str):
    page = page.strip("/")
    f1 = PAGES / f"{page}.html"
    if f1.is_file():
        # ex.: pages/team/members.html
        return render_template(f"pages/{page}.html")
    f2 = PAGES / page / "index.html"
    if f2.is_file():
        # ex.: pages/team/members/index.html
        rel = f2.relative_to(TEMPLATES).as_posix()
        return render_template(rel)
    return abort(404)

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
