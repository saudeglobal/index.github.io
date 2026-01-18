from __future__ import annotations

from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]

HTML_FILES = list(ROOT.rglob("*.html"))

def extract_tag(html: str, pattern: str) -> str | None:
    m = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else None

def extract_all_imgs_without_alt(html: str) -> int:
    # conta <img ...> sem alt= ou com alt=""
    imgs = re.findall(r"<img\b[^>]*>", html, flags=re.IGNORECASE)
    bad = 0
    for tag in imgs:
        alt = re.search(r'\balt\s*=\s*"(.*?)"', tag, flags=re.IGNORECASE)
        if not alt or alt.group(1).strip() == "":
            bad += 1
    return bad

def main() -> None:
    rows = []
    for f in HTML_FILES:
        # ignora pastas que você não quer auditar, se necessário
        # exemplo: if "node_modules" in str(f): continue
        html = f.read_text(encoding="utf-8", errors="ignore")

        title = extract_tag(html, r"<title>(.*?)</title>")
        desc = extract_tag(html, r'<meta\s+name="description"\s+content="(.*?)"')
        canon = extract_tag(html, r'<link\s+rel="canonical"\s+href="(.*?)"')
        h1 = extract_tag(html, r"<h1[^>]*>(.*?)</h1>")

        imgs_no_alt = extract_all_imgs_without_alt(html)

        issues = []
        if not title: issues.append("missing_title")
        if not desc: issues.append("missing_description")
        if not canon: issues.append("missing_canonical")
        if not h1: issues.append("missing_h1")

        if title and len(title) > 60: issues.append("title_too_long")
        if desc and len(desc) > 160: issues.append("description_too_long")
        if imgs_no_alt > 0: issues.append(f"images_missing_alt:{imgs_no_alt}")

        rows.append({
            "file": str(f.relative_to(ROOT)),
            "title": title or "",
            "description": desc or "",
            "canonical": canon or "",
            "h1": re.sub(r"<.*?>", "", h1 or ""),  # remove tags internos se houver
            "issues": ",".join(issues),
        })

    out = ROOT / "seo_report.csv"
    with out.open("w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=["file","title","description","canonical","h1","issues"])
        w.writeheader()
        w.writerows(rows)

    print(f"[OK] SEO report written: {out} ({len(rows)} files)")

if __name__ == "__main__":
    main()
