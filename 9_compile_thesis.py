"""
9_compile_thesis.py
Merges thesis_results.md into thesis.md, writes thesis_final.md.
Optionally converts to DOCX via pandoc.

Usage:
    python 9_compile_thesis.py
    python 9_compile_thesis.py --no-pandoc
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from config import (
    THESIS_PATH, THESIS_RESULTS_PATH as RESULTS_MD_PATH,
    THESIS_FINAL_PATH, REFERENCES_APA_PATH, REFERENCE_DOCX,
    DOCX_OUTPUT, TABLES_DIR,
    append_run_log, _sha256_file,
)

_RESULTS_PATTERN  = re.compile(
    r"<!-- RESULTS:BEGIN:(\w+) -->\n(.*?)\n<!-- RESULTS:END:\1 -->",
    re.DOTALL,
)
_PLACEHOLDER_PATTERN = re.compile(
    r"<!-- PLACEHOLDER:(\w+) -->\n.*?\n<!-- /PLACEHOLDER:\1 -->",
    re.DOTALL,
)


def parse_results_blocks(results_md: str) -> dict[str, str]:
    """Extract all RESULTS:BEGIN/END blocks from thesis_results.md."""
    blocks: dict[str, str] = {}
    for m in _RESULTS_PATTERN.finditer(results_md):
        section_id = m.group(1)
        content    = m.group(2).strip()
        blocks[section_id] = content
    return blocks


def load_pca_block() -> str | None:
    """Read pca_diagnostics.json and return the formatted markdown block, or None if unavailable."""
    pca_path = TABLES_DIR / "pca_diagnostics.json"
    if not pca_path.exists():
        return None
    with open(pca_path, encoding="utf-8") as fh:
        d = json.load(fh)

    ev   = d["eigenvalue_pc1"]
    vpct = d["variance_explained_pct"]
    ld   = d["loadings"]
    n    = d["n_scenarios"]

    lines = [
        "**Table 5.2**",
        "",
        "*Shock Score PCA Diagnostics — First Principal Component*",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Eigenvalue (PC1) | {ev:.4f} |",
        f"| Variance explained | {vpct:.2f}% |",
        f"| Loading — Article Count | {ld['AC_e']:.4f} |",
        f"| Loading — Sentiment Extremity | {ld['SE_e']:.4f} |",
        f"| Loading — Attention Intensity | {ld['AI_e']:.4f} |",
        f"| Loading — Event-Type Severity | {ld['ES_raw']:.4f} |",
        f"| Scenarios used | {n} |",
        "",
        "*Note.* PC1 = first principal component of the four standardised Shock Score components.",
    ]
    return "\n".join(lines)


def load_references() -> str:
    """Parse references_apa.md and return its pre-formatted APA entries, sorted alphabetically.

    Reads the markdown table in references_apa.md and emits the ready-made
    `apa_formatted` column for each entry, sorted alphabetically (by author surname).
    """
    if not REFERENCES_APA_PATH.exists():
        return ""

    lines = REFERENCES_APA_PATH.read_text(encoding="utf-8").splitlines()

    apa_col: int | None = None
    entries: list[str] = []

    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # Header row: locate the apa_formatted column.
        if apa_col is None:
            if "apa_formatted" in cells:
                apa_col = cells.index("apa_formatted")
            continue
        # Separator row (| --- | --- | ...).
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue
        if apa_col >= len(cells):
            continue
        entry = cells[apa_col].strip()
        if entry:
            entries.append(entry)

    entries.sort(key=str.lower)
    return "\n\n".join(entries)


def merge(thesis_text: str, results_blocks: dict[str, str]) -> tuple[str, int, list[str]]:
    """
    Replace each PLACEHOLDER block in thesis_text with the matching results content.
    Returns (merged_text, n_replaced, not_found_ids).
    """
    n_replaced = 0
    not_found  = []

    def replacer(m: re.Match) -> str:
        nonlocal n_replaced
        sid = m.group(1)
        if sid in results_blocks:
            n_replaced += 1
            return results_blocks[sid]
        not_found.append(sid)
        return m.group(0)  # leave unchanged

    merged = _PLACEHOLDER_PATTERN.sub(replacer, thesis_text)

    # Report any results blocks that had no matching placeholder
    for sid in results_blocks:
        if f"<!-- PLACEHOLDER:{sid} -->" not in thesis_text:
            not_found.append(f"[no placeholder in thesis.md for: {sid}]")

    return merged, n_replaced, not_found


# Captures an APA label line ("**Figure X.X**" / "**Table X.X**") and the
# italic title line that immediately follows it. Single-asterisk lookahead
# avoids matching bold-italic (***...***) runs.
LABEL_PATTERN = re.compile(
    r"\*\*((?:Figure|Table)\s+\d+\.\d+)\*\*"   # bold label
    r"\s*\n+"                                    # blank line(s)
    r"\*((?!\*).+?)\*",                          # italic title (single asterisks)
    re.MULTILINE,
)


def _format_list(items: list[tuple[str, str]]) -> str:
    """Render label/title pairs as a fixed-width, aligned list.

    Entries are separated by a blank line so each becomes its own paragraph;
    otherwise pandoc soft-wraps the consecutive lines into one block in DOCX.
    """
    if not items:
        return "_No items found._"
    max_label_len = max(len(label) for label, _ in items)
    return "\n\n".join(
        f"{label:<{max_label_len}}    {title}" for label, title in items
    )


def build_label_lists(merged: str) -> tuple[str, str]:
    """Extract Table and Figure labels+titles from merged text, in document order.

    Returns (tables_markdown, figures_markdown).
    """
    figures: list[tuple[str, str]] = []
    tables:  list[tuple[str, str]] = []
    for m in LABEL_PATTERN.finditer(merged):
        label = m.group(1).strip()
        title = m.group(2).strip()
        (figures if label.startswith("Figure") else tables).append((label, title))
    return _format_list(tables), _format_list(figures)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-pandoc", action="store_true",
                        help="Skip pandoc DOCX conversion even if pandoc is available")
    args, _ = parser.parse_known_args()

    # Validate inputs
    if not THESIS_PATH.exists():
        print(f"ERROR: {THESIS_PATH} not found.", file=sys.stderr)
        sys.exit(1)
    if not RESULTS_MD_PATH.exists():
        print(f"ERROR: {RESULTS_MD_PATH} not found. Run 8_statistical_analysis.py first.",
              file=sys.stderr)
        sys.exit(1)

    thesis_text  = THESIS_PATH.read_text(encoding="utf-8")
    results_md   = RESULTS_MD_PATH.read_text(encoding="utf-8")

    # Parse all results blocks
    results_blocks = parse_results_blocks(results_md)
    print(f"Found {len(results_blocks)} RESULTS blocks in {RESULTS_MD_PATH}:")
    for sid in results_blocks:
        print(f"  {sid}")

    # Inject PCA diagnostics block (sourced from pca_diagnostics.json, not thesis_results.md)
    pca_block = load_pca_block()
    if pca_block is not None:
        results_blocks["s5_pca_diagnostics"] = pca_block
        print("  s5_pca_diagnostics (from pca_diagnostics.json)")
    else:
        print("  WARNING: pca_diagnostics.json not found — s5_pca_diagnostics placeholder will not be replaced.")

    # Inject references block (sourced from references.md)
    references_content = load_references()
    if references_content:
        results_blocks["references"] = references_content
        print(f"  references (from references_apa.md, {references_content.count(chr(10) + chr(10)) + 1} entries)")
    else:
        print("  WARNING: references_apa.md not found or empty — references placeholder will not be replaced.")

    # Merge
    merged, n_replaced, not_found = merge(thesis_text, results_blocks)

    # Rewrite figure paths: thesis_results.md uses relative "figures/"
    # which resolves in the results/ context but breaks at the repo root.
    # Replace all ](figures/ with ](results/figures/ in the compiled output.
    merged = merged.replace("](figures/", "](results/figures/")

    # Pass 2 – derive List of Tables / List of Figures from the merged text
    # (they depend on compiled content, so cannot live in thesis_results.md).
    tables_md, figures_md = build_label_lists(merged)
    merged = merged.replace(
        "<!-- PLACEHOLDER:list_of_tables -->\n[To be populated by 9_compile_thesis.py]\n<!-- /PLACEHOLDER:list_of_tables -->",
        tables_md,
    )
    merged = merged.replace(
        "<!-- PLACEHOLDER:list_of_figures -->\n[To be populated by 9_compile_thesis.py]\n<!-- /PLACEHOLDER:list_of_figures -->",
        figures_md,
    )
    # These two placeholders are intentionally filled in Pass 2, not from
    # thesis_results.md, so drop them from the unmatched-placeholder report.
    not_found = [x for x in not_found if x not in ("list_of_tables", "list_of_figures")]

    # Write output
    THESIS_FINAL_PATH.write_text(merged, encoding="utf-8")

    print(f"\nReplaced: {n_replaced} placeholder(s)")
    if not_found:
        for msg in not_found:
            print(f"  WARNING – not found: {msg}")

    # Verify no residual [To be populated...] strings
    residual = re.findall(r"\[To be populated by 8_statistical_analysis\.py\]", merged)
    if residual:
        print(f"\nWARNING: {len(residual)} unreplaced '[To be populated...]' string(s) remain in {THESIS_FINAL_PATH}")
    else:
        print(f"\nVerification: no '[To be populated...]' strings remain in {THESIS_FINAL_PATH}.")

    print(f"Output written to {THESIS_FINAL_PATH}")

    # Pandoc conversion
    pandoc_used = False
    if args.no_pandoc:
        print("Pandoc conversion skipped (--no-pandoc).")
    else:
        try:
            import pypandoc
            _root = Path(__file__).parent
            _ref  = _root / REFERENCE_DOCX
            _src  = _root / THESIS_FINAL_PATH
            _out  = _root / DOCX_OUTPUT
            extra_args = [f"--reference-doc={_ref}"] if _ref.exists() else []
            if not _ref.exists():
                print(f"Note: reference DOCX not found at {_ref} – using pandoc defaults.")
            pypandoc.convert_file(str(_src), "docx", outputfile=str(_out), extra_args=extra_args)
            print(f"DOCX written to {DOCX_OUTPUT}")
            pandoc_used = True
        except ImportError:
            print("Note: pypandoc not installed – DOCX conversion skipped.")
        except Exception as e:
            print(f"pandoc error: {e}", file=sys.stderr)

    append_run_log(
        script="9_compile_thesis.py",
        parameters={"pandoc_used": pandoc_used},
        inputs=[
            {"file": str(THESIS_PATH),       "sha256": _sha256_file(THESIS_PATH)},
            {"file": str(RESULTS_MD_PATH),   "sha256": _sha256_file(RESULTS_MD_PATH)},
            {"file": str(REFERENCES_APA_PATH), "sha256": _sha256_file(REFERENCES_APA_PATH)},
        ],
        outputs=[
            {"file": str(THESIS_FINAL_PATH), "rows": None,
             "sha256": _sha256_file(THESIS_FINAL_PATH)},
        ],
        notes=f"{n_replaced} placeholders replaced. {len(not_found)} not found.",
    )


if __name__ == "__main__":
    main()
