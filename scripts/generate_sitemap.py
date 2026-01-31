# scripts/generate_sitemap.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import os

BASE_URL = os.environ.get("BASE_URL", "https://saudenaturalglobal.com.br").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]  # raiz do repo

# Arquivos que NÃO devem entrar no sitemap
EXCLUDE_FILES = {
    "index2.html",      # rascunho
    "404.html",
}

# Pastas que NÃO devem entrar no sitemap
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "content_pipeline",
    "seo_audit",
    "analytics_report",
    "scripts",          # <-- importante: não indexar scripts
}

# Se o nome do arquivo contiver algo disso, exclui
EXCLUDE_NAME_CONTAINS = {
    "test", "teste", "draft", "rascunho", "tmp", "backup", "old"
}

def should_exclude(path: Path) -> bool:
    rel = path.relative_to(ROOT)

    # exclui se estiver em diretório bloqueado
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return True

    # exclui arquivos específicos
    if path.name in EXCLUDE_FILES:
        return True

    # exclui por termos no nome
    lname = path.name.lower()
    if any(term in lname for term in EXCLUDE_NAME_CONTAINS):
        return True

    # não colocar arquivos ocultos (ex: .something.html)
    if any(part.startswith(".") for part in rel.parts):
        return True

    return False

def iter_html_files(root: Path):
    for p in root.rglob("*.html"):
        if should_exclude(p):
            continue
        yield p

def url_for_file(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()  # ex: artigos/index.html

    # Regra: qualquer ".../index.html" vira ".../"
    if rel.endswith("/index.html"):
        rel_dir = rel[: -len("index.html")]  # mantém a barra final
        return f"{BASE_URL}/{rel_dir}".replace("//", "/").replace(":/", "://")

    # Regra: "index.html" na raiz vira "/"
    if rel == "index.html":
        return f"{BASE_URL}/"

    return f"{BASE_URL}/{rel}"

def lastmod_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")

def build_sitemap_xml() -> str:
    urls = []
    for f in sorted(iter_html_files(ROOT)):
        loc = url_for_file(f)
        urls.append((loc, lastmod_iso(f)))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"

def ensure_robots_txt():
    robots_path = ROOT / "robots.txt"
    sitemap_line = f"Sitemap: {BASE_URL}/sitemap.xml"

    # Conteúdo base
    content = [
        "User-agent: *",
        "Allow: /",
        "",
        "Disallow: /content_pipeline/",
        "Disallow: /seo_audit/",
        "Disallow: /analytics_report/",
        "Disallow: /scripts/",        # <-- importante
        "Disallow: /.github/",        # <-- opcional, mas bom
        "",
        sitemap_line,
        "",
    ]

    # Se já existir robots, preserva as linhas que NÃO conflitam e força o Sitemap certo
    if robots_path.exists():
        old = robots_path.read_text(encoding="utf-8").splitlines()
        # pega linhas "custom" antigas (sem duplicar as principais)
        keep = []
        for line in old:
            l = line.strip().lower()
            if l.startswith("sitemap:"):
                continue
            if l in {"user-agent: *", "allow: /"}:
                continue
            if l.startswith("disallow: /content_pipeline/"):
                continue
            if l.startswith("disallow: /seo_audit/"):
                continue
            if l.startswith("disallow: /analytics_report/"):
                continue
            if l.startswith("disallow: /scripts/"):
                continue
            if l.startswith("disallow: /.github/"):
                continue
            keep.append(line)
        # reconstroi
        content = content[:-2] + keep + ["", sitemap_line, ""]

    robots_path.write_text("\n".join(content).strip() + "\n", encoding="utf-8")

def main():
    (ROOT / "sitemap.xml").write_text(build_sitemap_xml(), encoding="utf-8")
    ensure_robots_txt()
    print("OK: sitemap.xml e robots.txt atualizados.")

if __name__ == "__main__":
    main()
