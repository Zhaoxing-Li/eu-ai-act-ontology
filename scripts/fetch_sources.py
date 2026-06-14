"""Fetch and segment the EU AI Act (Regulation (EU) 2024/1689).

Downloads the official consolidated HTML from EUR-Lex (CELEX 32024R1689) and
segments it into articles and annexes. Each segment carries its article/annex
identifier and verbatim text, so every modelled element can later be traced to
a locatable source span.

Output: data/ai-act-raw.html, data/ai-act-segments.json
"""
import json
import re
import sys
import warnings
from pathlib import Path

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "ai-act-raw.html"
SEGMENTS = DATA / "ai-act-segments.json"

EURLEX_URL = (
    "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689"
)
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
)


def fetch() -> str:
    if RAW.exists() and RAW.stat().st_size > 200_000:
        return RAW.read_text(encoding="utf-8")
    print("Downloading EU AI Act from EUR-Lex ...")
    r = requests.get(EURLEX_URL, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    RAW.write_text(r.text, encoding="utf-8")
    return r.text


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def segment(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    # Flatten the relevant block-level elements in document order.
    blocks = soup.find_all(["p", "div", "table"], recursive=True)

    segments = []
    current = None  # dict being built

    def flush():
        if current and current["text"].strip():
            current["text"] = current["text"].strip()
            segments.append(current)

    seen_annex = False
    for el in blocks:
        cls = el.get("class") or []
        txt = norm(el.get_text(" ", strip=True))
        if not txt:
            continue

        # Article boundary: <p class="oj-ti-art"> holds "Article N"
        if "oj-ti-art" in cls:
            m = re.match(r"Article\s+(\d+)", txt)
            if m:
                flush()
                current = {
                    "type": "article",
                    "id": f"Article {m.group(1)}",
                    "number": int(m.group(1)),
                    "title": "",
                    "text": "",
                }
                continue

        # Article subtitle: the article's name
        if "oj-sti-art" in cls and current and current["type"] == "article" and not current["title"]:
            current["title"] = txt
            continue

        # Annex boundary: <p class="oj-doc-ti"> holds "ANNEX <ROMAN>"
        if "oj-doc-ti" in cls:
            m = re.match(r"ANNEX\s+([IVXLC]+)\b", txt)
            if m:
                flush()
                seen_annex = True
                current = {
                    "type": "annex",
                    "id": f"Annex {m.group(1)}",
                    "number": m.group(1),
                    "title": "",
                    "text": "",
                }
                continue

        # Accumulate body text into the current segment (skip page furniture).
        if current is not None:
            # avoid duplicating nested table text: only take leaf-ish blocks
            if el.find(["p", "div", "table"]) is None:
                current["text"] += txt + "\n"

    flush()
    # De-duplicate: keep only article/annex segments, drop empties.
    segments = [s for s in segments if s["text"].strip()]
    return segments


def main():
    html = fetch()
    segments = segment(html)
    DATA.mkdir(exist_ok=True)
    SEGMENTS.write_text(json.dumps(segments, indent=2, ensure_ascii=False), encoding="utf-8")

    arts = [s for s in segments if s["type"] == "article"]
    annexes = [s for s in segments if s["type"] == "annex"]
    print(f"Segments: {len(segments)}  (articles={len(arts)}, annexes={len(annexes)})")
    # Acceptance checks
    by_id = {s["id"]: s for s in segments}
    assert "Article 5" in by_id, "Article 5 (prohibited practices) missing"
    assert "Annex III" in by_id, "Annex III (high-risk domains) missing"
    print("OK: Article 5 ->", by_id["Article 5"]["title"][:60])
    print("OK: Annex III  ->", by_id["Annex III"]["title"][:60], "| len", len(by_id["Annex III"]["text"]))


if __name__ == "__main__":
    sys.exit(main())
