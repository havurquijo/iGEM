from pathlib import Path
from flask import Flask, render_template, abort
from flask_frozen import Freezer

BASE_DIR = Path(__file__).resolve().parent
template_folder = BASE_DIR / "wiki"
static_folder   = BASE_DIR / "static"

app = Flask(
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder),      # <- aponta para ./static
    static_url_path="/static"
)

app.config.update(
    FREEZER_DESTINATION="public",
    FREEZER_RELATIVE_URLS=True,
    FREEZER_IGNORE_MIMETYPE_WARNINGS=True,
)

freezer = Freezer(app)

@app.cli.command("freeze")
def freeze_cmd():
    freezer.freeze()

@app.cli.command("serve")
def serve_cmd():
    freezer.run()

@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route('/<path:page>', endpoint='pages')
def pages_route(page: str):
    pages_dir = template_folder / "pages"
    # 1) tenta pages/<page>.html
    file1 = pages_dir / f"{page}.html"
    if file1.is_file():
        rel = file1.relative_to(template_folder).as_posix()
        return render_template(rel)

    # 2) tenta pages/<page>/index.html
    file2 = pages_dir / page / "index.html"
    if file2.is_file():
        rel = file2.relative_to(template_folder).as_posix()
        return render_template(rel)

    return abort(404)

# === Generator: emite URLs para todos os .html em wiki/pages
@freezer.register_generator
def pages():
    pages_dir = template_folder / "pages"
    for f in pages_dir.rglob("*.html"):
        rel = f.relative_to(pages_dir).as_posix()
        if rel == "home.html":
            continue
        if rel.endswith("/index.html"):
            # "team/index.html" -> "team"
            yield {"page": rel[:-len("/index.html")]}
        else:
            # "docs/intro.html" -> "docs/intro"
            yield {"page": rel[:-5]}

if __name__ == "__main__":
    app.run(port=8080)
