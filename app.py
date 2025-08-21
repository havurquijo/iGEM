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

# rota espera .html
@app.route('/<path:page>.html', endpoint='pages')
def pages_route(page):  # não mude o nome do endpoint
    pages_dir = template_folder / "pages"
    file1 = pages_dir / f"{page}.html"
    if file1.is_file():
        rel = file1.relative_to(template_folder).as_posix()
        return render_template(rel)
    return abort(404)

# generator emite .../algo.html
@freezer.register_generator
def pages():
    pages_dir = template_folder / "pages"
    for f in pages_dir.rglob("*.html"):
        rel = f.relative_to(pages_dir).as_posix()
        if rel == "home.html":
            continue
        yield {"page": rel[:-5]}  # remove ".html" -> url será .../<page>.html


if __name__ == "__main__":
    app.run(port=8080)
