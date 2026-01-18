from __future__ import annotations
import csv
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
OUTPUT = os.path.join(BASE_DIR, "analytics_report", "seo_report.csv")

def iter_html_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".html"):
                yield os.path.join(dirpath, fn)

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def audit_html(path: str) -> dict:
    html = read_file(path)
    soup = BeautifulSoup(html, "lxml")

    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = desc_tag.get("content", "").strip() if desc_tag else ""

    canon = soup.find("link", rel=lambda x: x and "canonical" in x)
    canonical = canon.get("href", "").strip() if canon else ""

    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h1 = h1s[0] if h1s else ""

    imgs = soup.find_all("img")
    imgs_missing_alt = 0
    for img in imgs:
        alt = img.get("alt")
        if alt is None or not str(alt).strip():
            imgs_missing_alt += 1

    # links internos quebrados (simples: checa se arquivo existe no repo)
    broken_internal = 0
    for a in soup.find_all("a"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        if href.startswith("http") or href.startswith("mailto:") or href.startswith("#"):
            continue
        # normaliza
        href_clean = href.split("#")[0].split("?")[0]
        if href_clean.startswith("/"):
            href_clean = href_clean[1:]
        target = os.path.join(BASE_DIR, href_clean)
        # só checa se parece arquivo html
        if href_clean.endswith(".html") and not os.path.exists(target):
            broken_internal += 1

    issues = []
    if not title: issues.append("missing_title")
    if len(title) > 70: issues.append("title_too_long")
    if not desc: issues.append("missing_description")
    if len(desc) > 160: issues.append("description_too_long")
    if not canonical: issues.append("missing_canonical")
    if len(h1s) == 0: issues.append("missing_h1")
    if len(h1s) > 1: issues.append("multiple_h1")
    if imgs_missing_alt > 0: issues.append(f"images_missing_alt:{imgs_missing_alt}")
    if broken_internal > 0: issues.append(f"broken_internal_links:{broken_internal}")

    return {
        "file": os.path.relpath(path, BASE_DIR),
        "title": title,
        "description_len": len(desc),
        "canonical": canonical,
        "h1": h1,
        "h1_count": len(h1s),
        "images": len(imgs),
        "images_missing_alt": imgs_missing_alt,
        "broken_internal_links": broken_internal,
        "issues": ";".join(issues) if issues else ""
    }

def main():
    rows = []
    for path in iter_html_files(BASE_DIR):
        # ignore node_modules etc se existirem
        if ".git" in path:
            continue
        rows.append(audit_html(path))

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["file"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"OK: gerado {OUTPUT} com {len(rows)} arquivos auditados.")

if __name__ == "__main__":
    main()
