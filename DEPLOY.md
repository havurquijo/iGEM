Instruções rápidas para congelar o site e publicar no GitHub Pages (pasta `docs/`)

Pré-requisitos
- Python 3.11+ (ou 3.10)
- virtualenv (recomendado)

Instalação (exemplo):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r dependencies.txt
```

Gerar site estático na pasta `docs/` (usa o freezer do Flask):

```bash
# opcional: limpar uma pasta docs/ existente
rm -rf docs/
# exportar destino para docs/
export FREEZER_DESTINATION=docs
# rodar verificação rápida
flask --app app.py verify
# congelar
flask --app app.py freeze
```

Publicar no GitHub (branch `main`, usar GitHub Pages -> Source: `docs/` folder):

```bash
git add docs/
git commit -m "Build site for GitHub Pages"
git push
```

Observações
- Se preferir GitHub Pages a partir da branch `gh-pages`, mantenha `FREEZER_DESTINATION` como `public` e publique a pasta `public/` usando o fluxo de `gh-pages`.
- Se encontrar erro `flask: command not found`, use `pip install Flask` ou ative o virtualenv.
