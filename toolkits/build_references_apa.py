"""
add_apa_citations.py
Reads references.md, queries CrossRef for each DOI, builds a structured
references_apa.md with explicit columns for every APA field plus author_key
(the original "Author and year" value) for mapping back to in-text citations.

6 entries that CrossRef cannot resolve are hardcoded at the bottom of this file
and appended to the output automatically.

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
DELAY = 0.3        # seconds between requests (CrossRef polite rate limit)
INPUT_FILE = "references.md"
OUTPUT_FILE = "references_apa.md"

OUTPUT_HEADERS = [
    "author_key",           # original "Author and year" from references.md — maps to in-text citations
    "authors_apa",          # e.g. "Moore, D. A., & Healy, P. J."
    "year",
    "title",
    "source_type",          # journal-article | book | posted-content | book-chapter | etc.
    "journal_or_publisher",
    "volume",
    "issue",
    "pages",
    "doi",
    "url",
    "missing_fields",       # comma-separated list of fields that could not be resolved
    "apa_formatted",        # final APA 7th edition string, ready to paste
]


# ---------------------------------------------------------------------------
# Hardcoded manual records — CrossRef could not resolve these 6 entries
# author_key must match the "Author and year" value in references.md exactly
# ---------------------------------------------------------------------------

MANUAL_RECORDS = [
    {
        "author_key":           "Jiang & Zhu, 2016",
        "authors_apa":          "Jiang, G. J., & Zhu, K. X.",
        "year":                 "2017",
        "title":                "Information shocks and short-term market underreaction",
        "source_type":          "journal-article",
        "journal_or_publisher": "Journal of Financial Economics",
        "volume":               "124",
        "issue":                "1",
        "pages":                "43\u201364",
        "doi":                  "10.1016/j.jfineco.2016.06.006",
        "url":                  "https://doi.org/10.1016/j.jfineco.2016.06.006",
        "missing_fields":       "manually resolved \u2014 year updated 2016\u21922017 (published JFE version); DOI added",
        "apa_formatted":        "Jiang, G. J., & Zhu, K. X. (2017). Information shocks and short-term market underreaction. *Journal of Financial Economics*, *124*(1), 43\u201364. https://doi.org/10.1016/j.jfineco.2016.06.006",
    },
    {
        "author_key":           "Kahneman et al., 2021",
        "authors_apa":          "Kahneman, D., Sibony, O., & Sunstein, C. R.",
        "year":                 "2021",
        "title":                "Noise: A flaw in human judgment",
        "source_type":          "book",
        "journal_or_publisher": "Little, Brown Spark",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "",
        "url":                  "https://www.worldcat.org/oclc/1242782025",
        "missing_fields":       "manually resolved \u2014 no DOI (book)",
        "apa_formatted":        "Kahneman, D., Sibony, O., & Sunstein, C. R. (2021). *Noise: A flaw in human judgment*. Little, Brown Spark.",
    },
    {
        "author_key":           "Huber et al., 2021",
        "authors_apa":          "Huber, C., Huber, J., & Kirchler, M.",
        "year":                 "2021",
        "title":                "Market shocks and professionals\u2019 investment behavior \u2013 Evidence from the COVID-19 crash",
        "source_type":          "journal-article",
        "journal_or_publisher": "Journal of Banking & Finance",
        "volume":               "133",
        "issue":                "",
        "pages":                "Article 106247",
        "doi":                  "10.1016/j.jbankfin.2021.106247",
        "url":                  "https://doi.org/10.1016/j.jbankfin.2021.106247",
        "missing_fields":       "manually resolved \u2014 authors_apa added; URL updated to published DOI",
        "apa_formatted":        "Huber, C., Huber, J., & Kirchler, M. (2021). Market shocks and professionals\u2019 investment behavior \u2013 Evidence from the COVID-19 crash. *Journal of Banking & Finance*, *133*, Article 106247. https://doi.org/10.1016/j.jbankfin.2021.106247",
    },
    {
        "author_key":           "Kahneman, 2011",
        "authors_apa":          "Kahneman, D.",
        "year":                 "2011",
        "title":                "Thinking, fast and slow",
        "source_type":          "book",
        "journal_or_publisher": "Farrar, Straus and Giroux",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "",
        "url":                  "https://www.worldcat.org/oclc/706020998",
        "missing_fields":       "manually resolved \u2014 no DOI (book)",
        "apa_formatted":        "Kahneman, D. (2011). *Thinking, fast and slow*. Farrar, Straus and Giroux.",
    },
    {
        "author_key":           "Cochrane, 2005",
        "authors_apa":          "Cochrane, J. H.",
        "year":                 "2005",
        "title":                "Asset pricing",
        "source_type":          "book",
        "journal_or_publisher": "Princeton University Press",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "",
        "url":                  "https://books.google.com/books/about/Asset_Pricing.html?id=20pmeMaKNwsC",
        "missing_fields":       "manually resolved \u2014 no DOI (book)",
        "apa_formatted":        "Cochrane, J. H. (2005). *Asset pricing* (Rev. ed.). Princeton University Press.",
    },
    {
        "author_key":           "Thaler & Sunstein, 2008",
        "authors_apa":          "Thaler, R. H., & Sunstein, C. R.",
        "year":                 "2008",
        "title":                "Nudge: Improving decisions about health, wealth, and happiness",
        "source_type":          "book",
        "journal_or_publisher": "Yale University Press",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "",
        "url":                  "https://www.worldcat.org/oclc/191578377",
        "missing_fields":       "manually resolved \u2014 no DOI (book)",
        "apa_formatted":        "Thaler, R. H., & Sunstein, C. R. (2008). *Nudge: Improving decisions about health, wealth, and happiness*. Yale University Press.",
    },
{
        "author_key":           "RavenPack, 2011",
        "authors_apa":          "RavenPack",
        "year":                 "2011",
        "title":                "Introducing the RavenPack sentiment index",
        "source_type":          "report",
        "journal_or_publisher": "RavenPack",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "",
        "url":                  "https://www.ravenpack.com/research/introducing-ravenpack-sentiment-index",
        "missing_fields":       "manually resolved \u2014 no DOI (institutional white paper, RavenPack Research Series No. 2)",
        "apa_formatted":        "RavenPack. (2011). *Introducing the RavenPack sentiment index* (RavenPack Research Series No. 2). https://www.ravenpack.com/research/introducing-ravenpack-sentiment-index",
    },
    {
        "author_key":           "SIFMA, 2025",
        "authors_apa":          "SIFMA",
        "year":                 "2025",
        "title":                "Capital markets fact book 2025",
        "source_type":          "report",
        "journal_or_publisher": "Securities Industry and Financial Markets Association",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "",
        "url":                  "https://www.sifma.org/research/statistics/fact-book",
        "missing_fields":       "manually resolved \u2014 no DOI (annual statistical report)",
        "apa_formatted":        "SIFMA. (2025). *Capital markets fact book 2025*. Securities Industry and Financial Markets Association. https://www.sifma.org/research/statistics/fact-book",
    },
    {
        "author_key":           "Swiss Business School, 2026",
        "authors_apa":          "Swiss Business School",
        "year":                 "2026",
        "title":                "Master\u2019s thesis handbook AY 2025\u201326",
        "source_type":          "internal-document",
        "journal_or_publisher": "Swiss Business School",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "",
        "url":                  "",
        "missing_fields":       "manually resolved \u2014 no DOI (unpublished internal document)",
        "apa_formatted":        "Swiss Business School. (2026). *Master\u2019s thesis handbook AY 2025\u201326* (C.S.4. v1.8) [Unpublished internal document]. Swiss Business School.",
    },
{
        "author_key":           "Hodgkinson et al., 1999",
        "authors_apa":          "Hodgkinson, G. P., Bown, N. J., Maule, A. J., Glaister, K. W., & Pearman, A. D.",
        "year":                 "1999",
        "title":                "Breaking the frame: An analysis of strategic cognition and decision making under uncertainty",
        "source_type":          "journal-article",
        "journal_or_publisher": "Strategic Management Journal",
        "volume":               "20",
        "issue":                "10",
        "pages":                "977\u2013985",
        "doi":                  "10.1002/(SICI)1097-0266(199910)20:10<977::AID-SMJ58>3.0.CO;2-X",
        "url":                  "https://doi.org/10.1002/(SICI)1097-0266(199910)20:10<977::AID-SMJ58>3.0.CO;2-X",
        "missing_fields":       "manually resolved \u2014 legacy pre-2000 Wiley DOI, CrossRef returns 404",
        "apa_formatted":        "Hodgkinson, G. P., Bown, N. J., Maule, A. J., Glaister, K. W., & Pearman, A. D. (1999). Breaking the frame: An analysis of strategic cognition and decision making under uncertainty. *Strategic Management Journal*, *20*(10), 977\u2013985. https://doi.org/10.1002/(SICI)1097-0266(199910)20:10<977::AID-SMJ58>3.0.CO;2-X",
    },
    {
        "author_key":           "Yang et al., 2020",
        "authors_apa":          "Yang, Y., UY, M. C. S., & Huang, A.",
        "year":                 "2020",
        "title":                "FinBERT: A pretrained language model for financial communications",
        "source_type":          "preprint",
        "journal_or_publisher": "arXiv",
        "volume":               "",
        "issue":                "",
        "pages":                "",
        "doi":                  "10.48550/arXiv.2006.08097",
        "url":                  "https://doi.org/10.48550/arXiv.2006.08097",
        "missing_fields":       "manually resolved \u2014 DataCite DOI (arXiv), not indexed by CrossRef",
        "apa_formatted":        "Yang, Y., UY, M. C. S., & Huang, A. (2020). *FinBERT: A pretrained language model for financial communications* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2006.08097",
    },
]

# Set of author_key values covered by MANUAL_RECORDS — used to skip these
# rows during the CrossRef pass so they are not duplicated in the output.
MANUAL_KEYS = {r["author_key"] for r in MANUAL_RECORDS}


# ---------------------------------------------------------------------------
# CrossRef helpers
# ---------------------------------------------------------------------------

def doi_from_url(url: str) -> str | None:
    """Extract DOI string from a doi.org URL or a bare DOI."""
    url = url.strip()
    m = re.search(r"(?:doi\.org/)(.+)", url, re.IGNORECASE)
    if m:
        return m.group(1).rstrip("/")
    if url.startswith("10."):
        return url
    return None


def fetch_crossref(doi: str) -> dict | None:
    """Return CrossRef works message dict for a DOI, or None on failure."""
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
# APA field extractors
# ---------------------------------------------------------------------------

def _format_author(author: dict) -> str:
    given = author.get("given", "").strip()
    family = author.get("family", "").strip()
    if not family:
        return author.get("name", "Unknown Author")
    if given:
        initials = " ".join(f"{p[0]}." for p in given.split() if p)
        return f"{family}, {initials}"
    return family


def _format_authors(authors: list[dict]) -> str:
    if not authors:
        return ""
    formatted = [_format_author(a) for a in authors]
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


def _get_year(msg: dict) -> str:
    for field in ("published-print", "published-online", "issued"):
        dp = msg.get(field, {}).get("date-parts", [[]])
        if dp and dp[0]:
            return str(dp[0][0])
    return ""


def _get_pages(msg: dict) -> str:
    p = msg.get("page", "")
    return re.sub(r"[-–—]+", "\u2013", p.strip()) if p else ""


def _sentence_case(title_parts: list) -> str:
    title = " ".join(title_parts).strip()
    if not title:
        return ""
    lowered = title[0].upper() + title[1:].lower() if len(title) > 1 else title.upper()
    lowered = re.sub(r"(:\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), lowered)
    return lowered


def crossref_to_row(author_key: str, original_url: str, msg: dict) -> dict:
    """
    Build an output row dict from a CrossRef message.
    Missing fields are recorded in the missing_fields column.
    """
    doc_type  = msg.get("type", "unknown")
    authors   = _format_authors(msg.get("author", []))
    year      = _get_year(msg)
    title     = _sentence_case(msg.get("title", [""]))
    doi       = msg.get("DOI", "")
    doi_link  = f"https://doi.org/{doi}" if doi else original_url.strip()
    volume    = msg.get("volume", "")
    issue     = msg.get("issue", "")
    pages     = _get_pages(msg)

    if doc_type == "journal-article":
        journal = (msg.get("container-title") or [""])[0]
        pub     = journal
    elif doc_type in ("monograph", "book", "reference-book"):
        pub     = msg.get("publisher", "")
    elif doc_type == "book-chapter":
        pub     = (msg.get("container-title") or [""])[0]
    elif doc_type in ("posted-content", "report", "working-paper"):
        inst    = msg.get("institution", [])
        pub     = inst[0].get("name", "") if inst else ""
    else:
        pub = (msg.get("container-title") or [""])[0] or msg.get("publisher", "")

    # Identify missing fields
    missing = []
    if not authors:
        missing.append("authors_apa")
    if not pub:
        missing.append("journal_or_publisher")
    if not doi:
        missing.append("doi")

    # Build apa_formatted
    apa = _build_apa_string(doc_type, authors, year, title, pub, volume, issue, pages, doi_link, msg)

    return {
        "author_key":           author_key,
        "authors_apa":          authors,
        "year":                 year,
        "title":                title,
        "source_type":          doc_type,
        "journal_or_publisher": pub,
        "volume":               volume,
        "issue":                issue,
        "pages":                pages,
        "doi":                  doi,
        "url":                  doi_link,
        "missing_fields":       ", ".join(missing),
        "apa_formatted":        apa,
    }


def _build_apa_string(doc_type, authors, year, title, pub, volume, issue, pages, doi_link, msg):
    vol_str = f", *{volume}*" if volume else ""
    iss_str = f"({issue})"    if issue  else ""
    pg_str  = f", {pages}"   if pages  else ""

    if doc_type == "journal-article":
        return f"{authors} ({year}). {title}. *{pub}*{vol_str}{iss_str}{pg_str}. {doi_link}"

    if doc_type in ("monograph", "book", "reference-book"):
        return f"{authors} ({year}). *{title}*. {pub}. {doi_link}"

    if doc_type == "book-chapter":
        editors  = _format_authors(msg.get("editor", [])) if msg.get("editor") else ""
        pg_str2  = f" (pp. {pages})" if pages else ""
        ed_str   = f" In {editors} (Ed.)," if editors else " In"
        return f"{authors} ({year}). {title}.{ed_str} *{pub}*{pg_str2}. {doi_link}"

    if doc_type in ("posted-content", "report", "working-paper"):
        number   = msg.get("article-number") or msg.get("number", "")
        num_str  = f" (Working Paper No. {number})" if number else ""
        pub_str  = f" {pub}." if pub else ""
        return f"{authors} ({year}). *{title}*{num_str}.{pub_str} {doi_link}"

    # Fallback
    pub_str = f" *{pub}*." if pub else ""
    return f"{authors} ({year}). {title}.{pub_str} {doi_link}"


# ---------------------------------------------------------------------------
# Markdown table helpers
# ---------------------------------------------------------------------------

def parse_md_table(text: str) -> tuple[list[str], list[list[str]]]:
    headers, rows = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"[-:]+", c) for c in cells if c):
            continue
        if not headers:
            headers = cells
        else:
            rows.append(cells)
    return headers, rows


def render_md_table(headers: list[str], rows: list[dict]) -> str:
    """Render a list-of-dicts as a markdown table using OUTPUT_HEADERS order."""
    n = len(headers)
    # Convert dicts to lists in header order
    data = [[str(row.get(h, "")) for h in headers] for row in rows]

    widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(cells):
        return "| " + " | ".join(cells[i].ljust(widths[i]) for i in range(n)) + " |"

    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([fmt(headers), sep] + [fmt(r) for r in data])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Reading {INPUT_FILE} ...")
    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = f.read()

    src_headers, src_rows = parse_md_table(raw)

    # Locate columns in source table
    try:
        key_idx = next(i for i, h in enumerate(src_headers) if "author" in h.lower())
        url_idx = next(i for i, h in enumerate(src_headers) if "url" in h.lower())
    except StopIteration:
        print("ERROR: Could not find required columns in source table.", file=sys.stderr)
        sys.exit(1)

    def get_cell(row, idx):
        return row[idx].strip() if idx < len(row) else ""

    output_rows = []
    total   = len(src_rows)
    ok      = 0
    skipped = 0
    failed  = 0

    for i, row in enumerate(src_rows):
        author_key = get_cell(row, key_idx)
        url        = get_cell(row, url_idx)

        # Manual records are appended separately — skip here to avoid duplicates
        if author_key in MANUAL_KEYS:
            print(f"[{i+1}/{total}] {author_key} — deferred to manual records")
            continue

        doi = doi_from_url(url)
        print(f"[{i+1}/{total}] {author_key} ...", end=" ", flush=True)

        if not doi:
            print("no DOI — skipped")
            output_rows.append({
                "author_key":           author_key,
                "authors_apa":          "",
                "year":                 "",
                "title":                get_cell(row, next((j for j, h in enumerate(src_headers) if "title" in h.lower()), 2)),
                "source_type":          "",
                "journal_or_publisher": "",
                "volume":               "",
                "issue":                "",
                "pages":                "",
                "doi":                  "",
                "url":                  url,
                "missing_fields":       "authors_apa, journal_or_publisher, doi — no DOI in source",
                "apa_formatted":        "",
            })
            skipped += 1
            continue

        msg = fetch_crossref(doi)
        if msg:
            output_rows.append(crossref_to_row(author_key, url, msg))
            print("OK")
            ok += 1
        else:
            output_rows.append({
                "author_key":           author_key,
                "authors_apa":          "",
                "year":                 "",
                "title":                "",
                "source_type":          "",
                "journal_or_publisher": "",
                "volume":               "",
                "issue":                "",
                "pages":                "",
                "doi":                  doi,
                "url":                  url,
                "missing_fields":       "all fields — CrossRef fetch failed",
                "apa_formatted":        "",
            })
            print("FAILED")
            failed += 1

        time.sleep(DELAY)

    # Append hardcoded manual records
    print(f"\nAppending {len(MANUAL_RECORDS)} manual records ...")
    output_rows.extend(MANUAL_RECORDS)

    print(f"\nSummary: {ok} OK | {skipped} skipped (no DOI) | {failed} failed | {len(MANUAL_RECORDS)} manual")
    print(f"Total rows: {len(output_rows)}")

    table = render_md_table(OUTPUT_HEADERS, output_rows)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(table + "\n")
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()