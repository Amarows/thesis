"""
add_apa_citations.py
Reads references.md, queries CrossRef for each DOI, builds APA 7th edition
citation string, adds an "APA Citation" column, writes updated references.md.

Run locally (requires internet access to api.crossref.org):
    python add_apa_citations.py

Dependencies: only stdlib (urllib, json, re, time)
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

CROSSREF_BASE = "https://api.crossref.org/works/"
DELAY = 0.3          # seconds between requests (CrossRef rate limit: 50 req/s polite)
INPUT_FILE = "references.md"
OUTPUT_FILE = "references.md"  # overwrites in place; back up first


# ---------------------------------------------------------------------------
# CrossRef helpers
# ---------------------------------------------------------------------------

def doi_from_url(url: str) -> str | None:
    """Extract DOI string from a doi.org URL or raw DOI."""
    url = url.strip()
    # Matches https://doi.org/..., http://dx.doi.org/..., https://dx.doi.org/...
    m = re.search(r"(?:doi\.org/)(.+)", url, re.IGNORECASE)
    if m:
        return m.group(1).rstrip("/")
    # Bare DOI pattern: 10.XXXX/...
    if url.startswith("10."):
        return url
    return None


def fetch_crossref(doi: str) -> dict | None:
    """Return CrossRef works JSON for a DOI, or None on failure."""
    url = CROSSREF_BASE + urllib.parse.quote(doi, safe="/()")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "thesis-apa-formatter/1.0 (mailto:your@email.com)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("message", {})
    except Exception as e:
        print(f"  WARN: CrossRef fetch failed for {doi!r}: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# APA 7th edition builder
# ---------------------------------------------------------------------------

def _format_author(author: dict) -> str:
    """Return 'Lastname, F. M.' from a CrossRef author dict."""
    given = author.get("given", "").strip()
    family = author.get("family", "").strip()
    if not family:
        # Institutional author or literal field
        return author.get("name", "Unknown Author")
    if given:
        initials = " ".join(f"{p[0]}." for p in given.split() if p)
        return f"{family}, {initials}"
    return family


def _format_authors(authors: list[dict]) -> str:
    """APA author list: Last, F. M., Last, F. M., & Last, F. M."""
    if not authors:
        return "Unknown Author"
    formatted = [_format_author(a) for a in authors]
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


def _get_year(msg: dict) -> str:
    """Extract publication year, preferring published-print > published-online > issued."""
    for field in ("published-print", "published-online", "issued"):
        dp = msg.get(field, {}).get("date-parts", [[]])
        if dp and dp[0]:
            return str(dp[0][0])
    return "n.d."


def _get_pages(msg: dict) -> str:
    """Return page range string like '502–523', normalising hyphens to en-dash."""
    p = msg.get("page", "")
    if p:
        return re.sub(r"[-–—]+", "–", p.strip())
    return ""


def _title_sentence_case(title_parts: list) -> str:
    """Join title parts and apply sentence case (first word + proper nouns left as-is)."""
    title = " ".join(title_parts).strip()
    if not title:
        return ""
    # Basic sentence case: lowercase everything after first char
    # (CrossRef titles are often all-caps or title-case; we lower then capitalise first)
    lowered = title[0].upper() + title[1:].lower() if len(title) > 1 else title.upper()
    # Re-capitalise after colon
    lowered = re.sub(r"(:\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), lowered)
    return lowered


def build_apa(msg: dict, original_url: str) -> str:
    """
    Build APA 7th edition citation string from a CrossRef message dict.
    Covers: journal article, book, chapter, working paper / preprint.
    """
    doc_type = msg.get("type", "")
    authors = _format_authors(msg.get("author", []))
    year = _get_year(msg)
    titles = msg.get("title", ["Untitled"])
    title = _title_sentence_case(titles)
    doi = msg.get("DOI", "")
    doi_link = f"https://doi.org/{doi}" if doi else original_url.strip()

    # Journal article (most common)
    if doc_type in ("journal-article",):
        journal = msg.get("container-title", [""])[0] if msg.get("container-title") else ""
        volume = msg.get("volume", "")
        issue = msg.get("issue", "")
        pages = _get_pages(msg)

        vol_str = f", *{volume}*" if volume else ""
        iss_str = f"({issue})" if issue else ""
        pg_str = f", {pages}" if pages else ""

        return f"{authors} ({year}). {title}. *{journal}*{vol_str}{iss_str}{pg_str}. {doi_link}"

    # Monograph / book
    if doc_type in ("monograph", "book", "reference-book"):
        publisher = msg.get("publisher", "")
        return f"{authors} ({year}). *{title}*. {publisher}. {doi_link}"

    # Book chapter
    if doc_type == "book-chapter":
        container = msg.get("container-title", [""])[0] if msg.get("container-title") else ""
        editors = _format_authors(msg.get("editor", [])) if msg.get("editor") else ""
        pages = _get_pages(msg)
        pg_str = f" (pp. {pages})" if pages else ""
        ed_str = f" In {editors} (Ed.)," if editors else " In"
        return f"{authors} ({year}). {title}.{ed_str} *{container}*{pg_str}. {doi_link}"

    # Posted content / preprint (SSRN, arXiv, NBER)
    if doc_type in ("posted-content", "report", "working-paper"):
        institution_list = msg.get("institution", [])
        institution = institution_list[0].get("name", "") if institution_list else ""
        # Try to get working paper number from SSRN/NBER article-number field
        number = msg.get("article-number") or msg.get("number", "")
        num_str = f" (Working Paper No. {number})" if number else ""
        inst_str = f" {institution}." if institution else ""
        return f"{authors} ({year}). *{title}*{num_str}.{inst_str} {doi_link}"

    # Fallback: generic
    container = ""
    if msg.get("container-title"):
        container = f" *{msg['container-title'][0]}*."
    return f"{authors} ({year}). {title}.{container} {doi_link}"


# ---------------------------------------------------------------------------
# Markdown table parser / updater
# ---------------------------------------------------------------------------

def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Return (headers, rows) from a markdown table."""
    headers, rows = [], []
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"[-:]+", c) for c in cells if c):
            continue  # separator row
        if not headers:
            headers = cells
        else:
            rows.append(cells)
    return headers, rows


def pad_row(cells: list[str], width: int) -> list[str]:
    while len(cells) < width:
        cells.append("")
    return cells[:width]


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    # Compute column widths
    n = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row[:n]):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells):
        return "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " |"

    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    lines = [fmt_row(headers), sep] + [fmt_row(pad_row(list(r), n)) for r in rows]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Reading {INPUT_FILE} ...")
    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = f.read()

    lines = raw.splitlines()
    headers, rows = parse_table(lines)

    # Identify column indices
    try:
        url_idx = next(i for i, h in enumerate(headers) if "url" in h.lower())
    except StopIteration:
        print("ERROR: Could not find URL column in table.", file=sys.stderr)
        sys.exit(1)

    APA_HEADER = "APA Citation"
    if APA_HEADER not in headers:
        headers.append(APA_HEADER)
        apa_idx = len(headers) - 1
        for row in rows:
            row.append("")
    else:
        apa_idx = headers.index(APA_HEADER)

    total = len(rows)
    success = 0
    skipped = 0

    for i, row in enumerate(rows):
        row = pad_row(row, len(headers))
        url = row[url_idx] if url_idx < len(row) else ""
        doi = doi_from_url(url)

        author_year = row[0] if row else ""
        print(f"[{i+1}/{total}] {author_year} ...", end=" ", flush=True)

        if not doi:
            print("no DOI – skipped")
            skipped += 1
            rows[i] = row
            continue

        msg = fetch_crossref(doi)
        if msg:
            apa = build_apa(msg, url)
            row[apa_idx] = apa
            print("OK")
            success += 1
        else:
            print("FAILED (kept empty)")

        rows[i] = row
        time.sleep(DELAY)

    print(f"\nDone: {success} OK, {skipped} skipped (no DOI), {total-success-skipped} failed.")

    updated = render_table(headers, rows)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(updated + "\n")
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
