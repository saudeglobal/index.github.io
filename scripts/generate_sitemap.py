# scripts/generate_sitemap.py
from pathlib import Path
from datetime import datetime, timezone
import os

# Base do site
BASE_URL = os.environ.get("BASE_URL", "https://saudenaturalglobal.com.br").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]

# Excluir arquivos específicos
EXCLUDE_FILES = {
    "index2.html",   # rascunho
    "404.html",
}

# Excluir diretórios técnicos/irrelevantes para indexação
EXCLUDE_DIRS = {
    ".git", ".github",
    "node_modules",
    "content_pipeline",
    "seo_audit",
    "analytics_report",
    "scripts",      # opcional: não listar nada dentro
    "assets", "img", "jp", "en",  # ajuste se quiser indexar subpastas
}

# Excluir qualquer arquivo cujo nome contenha isso
EXCLUDE_NAME_CONTAINS = {
    "test", "teste", "draft", "rascunho", "tmp", "backup", "old"
}


def should_exclude(path: Path) -> bool:
    rel = path.relative_to(ROOT)

    # diretórios excluídos
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return True

    # arquivos excluídos
    if path.name in EXCLUDE_FILES:
        return True

    # termos excluídos no nome
    lower = path.name.lower()
    if any(term in lower for term in EXCLUDE_NAME_CONTAINS):
        return True

    return False


def iter_html_files(root: Path):
    for p in root.rglob("*.html"):
        if should_exclude(p):
            continue
        yield p


def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()

    # Normaliza qualquer ".../index.html" para ".../"
    if rel.endswith("/index.html"):
        base = rel[:-len("index.html")]  # mantém a barra final
        # caso especial raiz
        if base == "":
            return f"{BASE_URL}/"
        return f"{BASE_URL}/{base}".replace("//", "/").replace(":/", "://")

    # index.html na raiz vira "/"
    if rel == "index.html":
        return f"{BASE_URL}/"

    return f"{BASE_URL}/{rel}".replace("//", "/").replace(":/", "://")


def lastmod_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def build_sitemap() -> str:
    # Usa dict para deduplicar URLs (caso apareçam equivalentes)
    url_map = {}

    for f in iter_html_files(ROOT):
        loc = url_for(f)
        url_map[loc] = lastmod_iso(f)

    urls = sorted(url_map.items())

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, lastmod in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def ensure_robots():
    robots = ROOT / "robots.txt"
    sitemap_line = f"Sitemap: {BASE_URL}/sitemap.xml"

    base_lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "Disallow: /content_pipeline/",
        "Disallow: /seo_audit/",
        "Disallow: /analytics_report/",
        # opcional:
        "Disallow: /scripts/",
    ]

    if robots.exists():
        content = robots.read_text(encoding="utf-8").splitlines()
        # remove qualquer linha antiga de Sitemap:
        content = [ln for ln in content if not ln.strip().lower().startswith("sitemap:")]
        # se estiver vazio ou muito “estranho”, substitui pelo base
        if len([ln for ln in content if ln.strip()]) < 2:
            content = base_lines
    else:
        content = base_lines

    # garante o sitemap no fim
    if content and content[-1].strip() != "":
        content.append("")
    content.append(sitemap_line)

    robots.write_text("\n".join(content).strip() + "\n", encoding="utf-8")


def main():
    (ROOT / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    ensure_robots()
    print("OK: sitemap.xml e robots.txt atualizados.")


if __name__ == "__main__":
    main()
