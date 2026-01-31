# scripts/generate_sitemap.py
from pathlib import Path
from datetime import datetime, timezone
import os

BASE_URL = os.environ.get("BASE_URL", "https://saudenaturalglobal.com.br").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_FILES = {
    "index2.html",
}
EXCLUDE_DIRS = {
    ".git", ".github", "assets", "img", "jp", "en",
    "content_pipeline", "seo_audit", "analytics_report",
}

def iter_html_files(root: Path):
    for p in root.rglob("*.html"):
        rel = p.relative_to(root)
        # pula diretórios excluídos
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if p.name in EXCLUDE_FILES:
            continue
        yield p

def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{rel}"

def lastmod_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")

def build_sitemap():
    urls = []
    for f in sorted(iter_html_files(ROOT)):
        urls.append((url_for(f), lastmod_iso(f)))

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

    if robots.exists():
        content = robots.read_text(encoding="utf-8").splitlines()
    else:
        content = ["User-agent: *", "Allow: /"]

    # garante que tenha a linha Sitemap
    if not any(line.strip().lower().startswith("sitemap:") for line in content):
        content.append(sitemap_line)
    else:
        # substitui por base_url atual
        content = [
            sitemap_line if line.strip().lower().startswith("sitemap:") else line
            for line in content
        ]

    robots.write_text("\n".join(content).strip() + "\n", encoding="utf-8")

def main():
    xml = build_sitemap()
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    ensure_robots()
    print("OK: sitemap.xml e robots.txt atualizados.")

if __name__ == "__main__":
    main()
