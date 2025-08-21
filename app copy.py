from pathlib import Path
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
    FREEZER_DESTINATION="public",
    FREEZER_RELATIVE_URLS=True,
    FREEZER_IGNORE_MIMETYPE_WARNINGS=True,
)
freezer = Freezer(app)

# Helper para links internos: sempre garante a barra final
@app.context_processor
def _helpers():
    def page_url(page: str) -> str:
        return (url_for('pages', page=page).rstrip('/') + '/')
    return dict(page_url=page_url)

@app.cli.command('freeze')
def freeze_cmd():
    freezer.freeze()

@app.route('/')
def home():
    return render_template('pages/home.html')

# Endpoint 'pages' (bate com o generator)
@app.route('/<path:page>', endpoint='pages')
def pages_route(page: str):
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

# Generator com o MESMO nome do endpoint: 'pages'
@freezer.register_generator
def pages():
    for f in PAGES.rglob("*.html"):
        rel = f.relative_to(PAGES).as_posix()
        if rel == "home.html":
            continue
        if rel.endswith("/index.html"):
            # team/members/index.html -> /team/members/
            yield {"page": rel[:-len("/index.html")]}
        else:
            # docs/intro.html -> /docs/intro
            yield {"page": rel[:-5]}

if __name__ == "__main__":
    app.run(port=8080)
