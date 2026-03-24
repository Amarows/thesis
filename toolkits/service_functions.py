"""
service_functions.py – Thesis project utility functions
========================================================

Reusable service utilities for the thesis project:

  - count_words               Word count in Markdown / text files
  - analyze_references        Reference age analysis from Markdown citation lists
  - convert_md_to_docx        Markdown → Word (.docx) conversion via Pandoc
  - generate_bibliography_xml Bibliography XML for Microsoft Word (APA style)

All public functions accept explicit Path arguments — no hardcoded project paths.

Quickstart
----------
    from pathlib import Path
    from toolkits.service_functions import (
        count_words,
        analyze_references,
        convert_md_to_docx,
        generate_bibliography_xml,
    )

    root = Path(__file__).resolve().parents[1]  # project root

    print(count_words(root / "thesis.md"))
    analyze_references(root / "references.md")
    convert_md_to_docx(root / "thesis.md", root / "documents" / "thesis.docx")
    generate_bibliography_xml(
        root / "references.md",
        root / "documents" / "bibliography.xml",
    )
"""

import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Word count
# ---------------------------------------------------------------------------

def count_words(file_path: Path) -> int:
    """Count words in a text or Markdown file.

    A *word* is a contiguous sequence of word characters that may contain
    internal apostrophes or hyphens (e.g., ``don't``, ``risk-adjusted``).

    Args:
        file_path: Path to the file to analyse.

    Returns:
        Integer word count.

    Example::

        from pathlib import Path
        from toolkits.service_functions import count_words

        wc = count_words(Path("thesis.md"))
        print(f"thesis.md has {wc} words")
    """
    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    tokens = re.findall(r"\b[\w'-]+\b", text)
    return len(tokens)

count_words("thesis.md")

# ---------------------------------------------------------------------------
# Reference analysis
# ---------------------------------------------------------------------------

def analyze_references(file_path: Path, current_year: Optional[int] = None) -> None:
    """Extract and analyse in-text citations from a Markdown file.

    Detects citations matching ``[Author, YYYY]`` or ``[Author, YYYY](url)``
    and prints:

    * Top 5 most-cited references.
    * A summary table grouping citations by age:
      < 6 years / 6–10 years / > 10 years.

    Args:
        file_path:    Path to the Markdown file to analyse.
        current_year: Reference year for age calculation.
                      Defaults to the current calendar year.

    Example::

        from pathlib import Path
        from toolkits.service_functions import analyze_references

        analyze_references(Path("thesis.md"))
        analyze_references(Path("thesis.md"), current_year=2025)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return

    if current_year is None:
        current_year = date.today().year

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    pattern = r'\[([^\]]*?\b(19\d{2}|20\d{2})\b[^\]]*?)\]'
    matches = re.findall(pattern, text)

    references: List[str] = []
    years: List[int] = []

    for match, year_str in matches:
        name_match = re.search(r'(.*?),\s*' + re.escape(year_str), match)
        ref_name = (
            name_match.group(1).strip() + f", {year_str}"
            if name_match
            else match.strip()
        )
        references.append(ref_name)
        years.append(int(year_str))

    print(f"\n--- Reference Analysis for {file_path.name} ---")

    top_5 = Counter(references).most_common(5)
    print("Top 5 references used:")
    for ref, cnt in top_5:
        print(f"  {ref}: {cnt}")

    age_groups = {
        "< 6 years old":   0,
        "6-10 years old":  0,
        "> 10 years old":  0,
    }
    for year in years:
        age = current_year - year
        if age < 6:
            age_groups["< 6 years old"] += 1
        elif age <= 10:
            age_groups["6-10 years old"] += 1
        else:
            age_groups["> 10 years old"] += 1

    total = len(years)
    print("\nReference age summary:")
    print(f"{'Age Group':<20} | {'Count':<6} | {'Share (%)':<10}")
    print("-" * 43)
    for group, cnt in age_groups.items():
        share = (cnt / total * 100) if total > 0 else 0
        print(f"{group:<20} | {cnt:<6} | {share:<10.2f}")
    print(f"{'Total':<20} | {total:<6} | {'100.00':<10}")

analyze_references("thesis.md")


# ---------------------------------------------------------------------------
# Markdown → DOCX conversion
# ---------------------------------------------------------------------------

def convert_md_to_docx(input_path: Path, output_path: Path) -> None:
    """Convert a Markdown file to a Word document (.docx) using Pandoc.

    Automatically downloads Pandoc if it is not found on the system.
    Output directory is created automatically if it does not exist.

    Args:
        input_path:  Path to the source ``.md`` file.
        output_path: Destination path for the ``.docx`` file.

    Example::

        from pathlib import Path
        from toolkits.service_functions import convert_md_to_docx

        convert_md_to_docx(
            Path("thesis.md"),
            Path("documents/thesis.docx"),
        )
    """
    import pypandoc  # optional dependency; imported lazily to avoid hard requirement

    try:
        pypandoc.get_pandoc_version()
    except OSError:
        print("Pandoc not found. Downloading...")
        pypandoc.download_pandoc()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pypandoc.convert_file(str(input_path), "docx", outputfile=str(output_path))
    print(f"Conversion complete: {output_path.resolve()}")


# ---------------------------------------------------------------------------
# Bibliography XML generation  (private helpers)
# ---------------------------------------------------------------------------

_NS_B = "http://schemas.openxmlformats.org/officeDocument/2006/bibliography"
ET.register_namespace("b", _NS_B)


def _normalize(s: str) -> str:
    """Collapse whitespace and strip a string."""
    return re.sub(r"\s+", " ", s or "").strip()


def _split_authors(author_year: str) -> Tuple[List[str], str]:
    """Parse ``"Author1 & Author2, 2008"`` → ``(["Author1", "Author2"], "2008")``."""
    s = _normalize(author_year)
    year = ""
    m = re.search(r"(\b19\d{2}\b|\b20\d{2}\b)", s)
    if m:
        year = m.group(1)
        s = _normalize(re.sub(r"[,;]?\s*" + re.escape(year) + r"\s*$", "", s))
    parts = re.split(r"\s*(?:&| and )\s*", s)
    authors = [_normalize(p) for p in parts if _normalize(p)]
    return authors, year


def _make_tag(author_year: str, title: str, url: str) -> str:
    """Generate a short alphanumeric tag for a bibliography entry."""
    base = re.sub(r"[^A-Za-z0-9]+", "_", _normalize(author_year + " " + title)).strip("_")
    if not base:
        base = re.sub(r"[^A-Za-z0-9]+", "_", _normalize(url)).strip("_")
    return base[:48] or "Ref"


def _parse_reference_table(md_text: str) -> List[dict]:
    """Extract rows from a GFM table with columns: Author and year | URL | Title | File Name."""
    lines = [ln.rstrip("\n") for ln in md_text.splitlines() if ln.strip()]
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and "Author" in ln and "URL" in ln and "Title" in ln:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("Could not find the references table header in the Markdown file.")

    rows = []
    for ln in lines[header_idx + 2:]:  # skip header + separator
        if not ln.strip().startswith("|"):
            continue
        cols = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cols) < 3 or cols[0].lower().startswith("---"):
            continue
        rows.append({
            "author_year": _normalize(cols[0]),
            "url":         _normalize(cols[1]) if len(cols) > 1 else "",
            "title":       _normalize(cols[2]) if len(cols) > 2 else "",
            "file_name":   _normalize(cols[3]) if len(cols) > 3 else "",
        })
    return rows


# ---------------------------------------------------------------------------
# Bibliography XML generation  (public)
# ---------------------------------------------------------------------------

def generate_bibliography_xml(references_md_path: Path, output_xml_path: Path) -> None:
    """Generate a Microsoft Word bibliography XML from a Markdown reference table.

    The input file must contain a GFM table with columns::

        | Author and year | URL | Title | File Name |

    Output is an APA-style ``Sources`` XML compatible with Word's built-in
    citation manager (Insert → Citations & Bibliography).

    Args:
        references_md_path: Path to the Markdown file containing the reference table.
        output_xml_path:    Destination path for the ``.xml`` file.
                            Parent directories are created automatically.

    Example::

        from pathlib import Path
        from toolkits.service_functions import generate_bibliography_xml

        generate_bibliography_xml(
            Path("references.md"),
            Path("documents/bibliography.xml"),
        )
    """
    references_md_path = Path(references_md_path)
    output_xml_path = Path(output_xml_path)

    if not references_md_path.exists():
        print(f"Skipping XML generation: {references_md_path} not found.")
        return

    rows = _parse_reference_table(references_md_path.read_text(encoding="utf-8"))

    sources = ET.Element(f"{{{_NS_B}}}Sources")
    sources.set("SelectedStyle", "\\APA.XSL")

    for r in rows:
        authors, year = _split_authors(r["author_year"])
        tag = _make_tag(r["author_year"], r["title"], r["url"])

        src = ET.SubElement(sources, f"{{{_NS_B}}}Source")
        ET.SubElement(src, f"{{{_NS_B}}}Tag").text = tag
        ET.SubElement(src, f"{{{_NS_B}}}SourceType").text = "JournalArticle"

        # Author block: Sources/Source/Author/Author/NameList/Person
        author_el = ET.SubElement(src, f"{{{_NS_B}}}Author")
        author_main = ET.SubElement(author_el, f"{{{_NS_B}}}Author")
        name_list = ET.SubElement(author_main, f"{{{_NS_B}}}NameList")

        for a in authors:
            tokens = a.split()
            last = tokens[-1] if tokens else a
            first = " ".join(tokens[:-1]) if len(tokens) > 1 else ""
            person = ET.SubElement(name_list, f"{{{_NS_B}}}Person")
            ET.SubElement(person, f"{{{_NS_B}}}Last").text = last
            if first:
                ET.SubElement(person, f"{{{_NS_B}}}First").text = first

        if year:
            ET.SubElement(src, f"{{{_NS_B}}}Year").text = year
        if r["title"]:
            ET.SubElement(src, f"{{{_NS_B}}}Title").text = r["title"]
        if r["url"]:
            ET.SubElement(src, f"{{{_NS_B}}}URL").text = r["url"]
        ET.SubElement(src, f"{{{_NS_B}}}Medium").text = "InternetSite"

    output_xml_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(sources).write(output_xml_path, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {output_xml_path.resolve()} with {len(rows)} sources.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Resolve project root relative to this file (toolkits/ → root)
    _root = Path(__name__).resolve().parent.parent

    _thesis = _root / "thesis.md"
    _references = _root / "references.md"
    _docx = _root / "documents" / "thesis.docx"
    _xml = _root / "documents" / "bibliography.xml"

    # Word count
    if _thesis.exists():
        print(f"thesis.md word count: {count_words(_thesis)}")

    # Reference analysis
    analyze_references(_references)

    # Uncomment to convert thesis Markdown → Word document:
    # convert_md_to_docx(_thesis, _docx)

    # Generate bibliography XML for Word
    generate_bibliography_xml(_references, _xml)
