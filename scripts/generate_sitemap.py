#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime, timezone
from urllib.parse import urljoin

import xml.etree.ElementTree as ET

# Pastas para IGNORAR (ajuste se quiser)
EXCLUDE_DIRS = {
    ".git", ".github",
    "assets", "img",
    "content_pipeline",
    "seo_audit", "analytics_report",
    "node_modules",
}

# Arquivos para IGNORAR
EXCLUDE_FILES = {
    "404.html",
}

def git_lastmod_iso(path: str) -> str:
    """
    Retorna a data do último commit do arquivo no formato ISO 8601 (ex: 2026-01-31T10:20:30+00:00).
    Requer checkout com fetch-depth: 0 no Actions.
    """
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", "--", path],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except Exception:
        pass
    # fallback: agora (não ideal, mas evita quebrar)
    return datetime.now(timezone.utc).isoformat()

def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        # remove dirs excluídas
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]

        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            if fn in EXCLUDE_FILES:
                continue

            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")

            # Ignore arquivos que comecem com "_" (drafts) se quiser
            if os.path.basename(rel).startswith("_"):
                continue

            yield rel

def main():
    base_url = os.environ.get("BASE_URL", "https://saudenaturalglobal.com.br").rstrip("/") + "/"
    root = os.environ.get("SITE_ROOT", ".")
    out_file = os.environ.get("SITEMAP_OUT", "sitemap.xml")

    # Monta XML
    urlset = ET.Element("urlset", attrib={"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})

    # (Opcional) garantir home primeiro
    home_url = base_url
    home = ET.SubElement(urlset, "url")
    ET.SubElement(home, "loc").text = home_url
    ET.SubElement(home, "lastmod").text = datetime.now(timezone.utc).date().isoformat()

    # Lista arquivos .html
    pages = sorted(set(iter_html_files(root)))

    for rel in pages:
        # transforma "index.html" em "/" e ".../index.html" em ".../"
        if rel == "index.html":
            loc = base_url
        elif rel.endswith("/index.html"):
            loc = urljoin(base_url, rel[:-10] + "/")  # remove "index.html"
        else:
            loc = urljoin(base_url, rel)

        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text = loc
        ET.SubElement(url_el, "lastmod").text = git_lastmod_iso(rel)

    # escreve formatado
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ", level=0)
    tree.write(out_file, encoding="utf-8", xml_declaration=True)

    print(f"[OK] sitemap gerado: {out_file} ({len(pages)+1} urls)")

if __name__ == "__main__":
    main()
