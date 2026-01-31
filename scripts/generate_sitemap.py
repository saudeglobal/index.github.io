#!/usr/bin/env python3
# scripts/generate_sitemap.py

from pathlib import Path
from datetime import datetime, timezone
import os


# =========================
# Config
# =========================
BASE_URL = os.environ.get("BASE_URL", "https://saudenaturalglobal.com.br").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]
SITEMAP_OUT = ROOT / "sitemap.xml"
ROBOTS_OUT = ROOT / "robots.txt"

# Arquivos que NÃO entram no sitemap
EXCLUDE_FILES = {
    "index2.html",   # rascunho
    "404.html",
}

# Pastas que NÃO entram no sitemap (técnicas / internas)
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "content_pipeline",
    "seo_audit",
    "analytics_report",
}

# Se quiser excluir também imagens/assets do sitemap (não é necessário pois filtramos .html)
# mas pode manter fora do crawl:
ROBOTS_DISALLOW_DIRS = {
    "/content_pipeline/",
    "/seo_audit/",
    "/analytics_report/",
}

# (Opcional) exclui qualquer arquivo que tenha estes termos no nome
EXCLUDE_NAME_CONTAINS = {
    "test", "teste", "draft", "rascunho", "tmp", "backup", "old"
}


# =========================
# Helpers
# =========================
def is_excluded(path: Path) -> bool:
    """Decide se um arquivo deve ser ignorado."""
    rel = path.relative_to(ROOT)
    # pula dirs excluídos
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return True

    name = path.name
    if name in EXCLUDE_FILES:
        return True

    low = name.lower()
    if any(token in low for token in EXCLUDE_NAME_CONTAINS):
        return True

    return False


def iter_html_files() -> list[Path]:
    """Lista arquivos .html que devem entrar no sitemap."""
    files = []
    for p in ROOT.rglob("*.html"):
        if is_excluded(p):
            continue
        files.append(p)
    return sorted(set(files))


def lastmod_iso(path: Path) -> str:
    """Lastmod baseado no mtime do arquivo (UTC)."""
    ts = path.stat().st_mtime
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def to_loc(rel_path: str) -> str:
    """
    Converte caminho relativo em URL canônica.
    - index.html (raiz) -> /
    - qualquer /index.html em subpasta -> /subpasta/
    - demais -> /arquivo.html
    """
    rel_path = rel_path.replace("\\", "/")

    if rel_path == "index.html":
        return f"{BASE_URL}/"

    if rel_path.endswith("/index.html"):
        rel_dir = rel_path[:-10]  # remove "/index.html"
        return f"{BASE_URL}/{rel_dir}/"

    return f"{BASE_URL}/{rel_path}"


def build_sitemap_xml() -> str:
    files = iter_html_files()

    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        loc = to_loc(rel)
        lastmod = lastmod_iso(f)

        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def ensure_robots_txt():
    """
    Garante um robots.txt mínimo com:
    - Allow /
    - Disallow das pastas técnicas
    - Sitemap apontando para /sitemap.xml
    """
    sitemap_line = f"Sitemap: {BASE_URL}/sitemap.xml"

    # base padrão
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
    ]

    # disallow pastas técnicas
    for d in sorted(ROBOTS_DISALLOW_DIRS):
        lines.append(f"Disallow: {d}")
    lines.append("")
    lines.append(sitemap_line)
    lines.append("")

    ROBOTS_OUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    xml = build_sitemap_xml()
    SITEMAP_OUT.write_text(xml, encoding="utf-8")
    ensure_robots_txt()
    print(f"OK: sitemap.xml gerado com {xml.count('<url>')} URLs e robots.txt atualizado.")


if __name__ == "__main__":
    main()
