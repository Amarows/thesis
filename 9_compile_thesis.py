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
import shutil
import subprocess
import sys

from config import (
    THESIS_PATH, THESIS_RESULTS_PATH as RESULTS_MD_PATH,
    THESIS_FINAL_PATH, REFERENCE_DOCX, DOCX_OUTPUT, TABLES_DIR,
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

    all_positive = all(v > 0 for v in ld.values())
    sign_note = (
        "All four components load positively on PC1, confirming that the composite "
        "represents a common factor of shock intensity rather than a contrast between components."
        if all_positive else
        "The loading signs indicate a mixed pattern; interpretation of the composite should "
        "account for the direction of individual component relationships."
    )

    lines = [
        "**Table 5.x: SC_total PCA Diagnostics — First Principal Component**",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Eigenvalue (PC1) | {ev:.4f} |",
        f"| Variance explained | {vpct:.2f}% |",
        f"| Loading — Article Count (AC_e) | {ld['AC_e']:.4f} |",
        f"| Loading — Sentiment Extremity (SE_e) | {ld['SE_e']:.4f} |",
        f"| Loading — Attention Intensity (AI_e) | {ld['AI_e']:.4f} |",
        f"| Loading — Event-Type Severity (ES_raw) | {ld['ES_raw']:.4f} |",
        f"| Scenarios used | {n} |",
        "",
        f"The eigenvalue of {ev:.4f} {'exceeds' if ev > 1.0 else 'does not exceed'} 1.0"
        f"{', satisfying the Kaiser criterion.' if ev > 1.0 else ', falling short of the Kaiser criterion.'} "
        f"The first principal component explains {vpct:.2f}% of the total variance across the four inputs. "
        f"{sign_note}",
    ]
    return "\n".join(lines)


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

    # Merge
    merged, n_replaced, not_found = merge(thesis_text, results_blocks)

    # Rewrite figure paths: thesis_results.md uses relative "figures/"
    # which resolves in the results/ context but breaks at the repo root.
    # Replace all ](figures/ with ](results/figures/ in the compiled output.
    merged = merged.replace("](figures/", "](results/figures/")

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
        pandoc = shutil.which("pandoc")
        if pandoc is None:
            print("Note: pandoc not found on PATH – DOCX conversion skipped.")
        else:
            cmd = [pandoc, str(THESIS_FINAL_PATH), "-o", str(DOCX_OUTPUT)]
            if REFERENCE_DOCX.exists():
                cmd += [f"--reference-doc={REFERENCE_DOCX}"]
            else:
                print(f"Note: reference DOCX not found at {REFERENCE_DOCX} – using pandoc defaults.")
            print(f"\nRunning: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"DOCX written to {DOCX_OUTPUT}")
                pandoc_used = True
            else:
                print(f"pandoc error:\n{result.stderr}", file=sys.stderr)

    append_run_log(
        script="9_compile_thesis.py",
        parameters={"pandoc_used": pandoc_used},
        inputs=[
            {"file": str(THESIS_PATH),       "sha256": _sha256_file(THESIS_PATH)},
            {"file": str(RESULTS_MD_PATH),   "sha256": _sha256_file(RESULTS_MD_PATH)},
        ],
        outputs=[
            {"file": str(THESIS_FINAL_PATH), "rows": None,
             "sha256": _sha256_file(THESIS_FINAL_PATH)},
        ],
        notes=f"{n_replaced} placeholders replaced. {len(not_found)} not found.",
    )


if __name__ == "__main__":
    main()
