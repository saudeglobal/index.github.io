from __future__ import annotations
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "content_pipeline", "data", "articles.json")
TPL_PATH = os.path.join(BASE_DIR, "content_pipeline", "templates", "article_template.html")
OUT_DIR = os.path.join(BASE_DIR, "artigos")

# 🔥 NOVO: pasta dos corpos HTML
BODY_DIR = os.path.join(BASE_DIR, "content_pipeline", "data", "article_bodies")

CANONICAL_DOMAIN = "https://saudenaturalglobal.com.br"


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def br_date(iso_date: str) -> str:
    d = datetime.strptime(iso_date, "%Y-%m-%d")
    return d.strftime("%d/%m/%Y")


def safe(s: str) -> str:
    return (s or "").replace("\r", "").strip()


# 🔥 NOVA FUNÇÃO (ESSENCIAL)
def get_body_html(article: dict) -> str:
    body_file = article.get("body_file")

    if body_file:
        body_path = os.path.join(BODY_DIR, body_file)

        if os.path.exists(body_path):
            with open(body_path, "r", encoding="utf-8") as f:
                return f.read()

        else:
            print(f"⚠️ body_file não encontrado: {body_path}")

    return safe(article.get("body_html"))


def render(template: str, ctx: dict) -> str:
    out = template
    for k, v in ctx.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def main() -> None:
    ensure_dirs()
    tpl = load_template(TPL_PATH)
    data = load_json(DATA_PATH)

    articles = data.get("articles", [])
    if not articles:
        raise SystemExit("Nenhum artigo encontrado em content_pipeline/data/articles.json")

    for a in articles:
        slug = safe(a.get("slug"))
        if not slug:
            raise SystemExit("Artigo sem 'slug' em articles.json")

        filename = f"{slug}.html"
        canonical = f"{CANONICAL_DOMAIN}/artigos/{filename}"

        date_modified = a.get("date_modified", datetime.utcnow().strftime("%Y-%m-%d"))

        # 🔥 AQUI É A MUDANÇA PRINCIPAL
        body_html = get_body_html(a)

        ctx = {
            "TITLE": safe(a.get("title")),
            "DESCRIPTION": safe(a.get("description")),
            "CANONONICAL": canonical,
            "CANONICAL": canonical,

            "OG_TITLE": safe(a.get("og_title") or a.get("title")),
            "OG_DESCRIPTION": safe(a.get("og_description") or a.get("description")),
            "OG_IMAGE": safe(a.get("og_image") or "https://images.unsplash.com/photo-1589923188900-85dae523342b?q=80&w=1600&auto=format&fit=crop"),

            "PILLAR": safe(a.get("pillar", "Conteúdo")),
            "H1": safe(a.get("h1") or a.get("title")),
            "INTRO": safe(a.get("intro")),
            "READ_TIME": safe(a.get("read_time", "6–8 min")),
            "DATE_MODIFIED": date_modified,
            "DATE_MODIFIED_BR": br_date(date_modified),

            # 🔥 AGORA VEM DO ARQUIVO OU FALLBACK
            "BODY_HTML": body_html,

            "EVIDENCE": safe(a.get("evidence")),
            "CTA_URL": safe(a.get("cta_url")),
        }

        html = render(tpl, ctx)
        out_path = os.path.join(OUT_DIR, filename)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"OK: gerado {out_path}")


if __name__ == "__main__":
    main()
