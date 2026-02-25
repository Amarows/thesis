import pypandoc

# If pandoc is not found, download it automatically
try:
    pypandoc.get_pandoc_version()
except OSError:
    print("Pandoc not found. Downloading...")
    pypandoc.download_pandoc()

# Define the input and output file names
input_file = '../thesis.md'
output_file = '../documents/thesis.docx'

# Convert markdown to docx
# The format 'docx' is automatically inferred from the output file extension
#pypandoc.convert_file(input_file, 'docx', outputfile=output_file)

print(f"Conversion complete: {output_file} has been created.")


# =========================================== word count ===========================================

# word count
import re
from pathlib import Path
from collections import Counter

def count_words_in_file(file_path: Path) -> int:
    """Count words in a text/Markdown file using a simple token regex.

    A word is defined as a sequence of letters/digits that may include
    internal apostrophes or hyphens (e.g., don't, risk-adjusted).
    """
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    # Use regex to match words while skipping most punctuation/Markdown symbols
    tokens = re.findall(r"\b[\w'-]+\b", text)
    return len(tokens)

repo_root = Path('').parent
thesis_path = repo_root / "thesis.md"

count = count_words_in_file(thesis_path)
print(f"thesis.md word count: {count}")


# =========================================== references age =========================================== 
def analyze_references(file_path: Path):
    """Extract and analyze references from a Markdown file.
    
    Prints top 5 references used and a summary table by age.
    """
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    
    # Pattern to match references starting with '[' and ending with ']',
    # e.g., [Author, Year] or [Author, Year](link) — we capture the bracket content.
    pattern = r'\[([^\]]*?\b(19\d{2}|20\d{2})\b[^\]]*?)\]'
    matches = re.findall(pattern, text)
    
    references = []
    years = []
    
    for match, year_str in matches:
        # Extract name part before the year for better identification
        # e.g., in "[Author, 2008](link)", name_match will get "Author"
        name_match = re.search(r'(.*?),\s*' + re.escape(year_str), match)
        if name_match:
            ref_name = name_match.group(1).strip() + f", {year_str}"
        else:
            ref_name = match.strip()
        
        references.append(ref_name)
        years.append(int(year_str))
    
    # Analysis based on current year 2026
    current_year = 2026
    
    print(f"\n--- Reference Analysis for {file_path.name} ---")
    
    # Top 5 references
    top_5 = Counter(references).most_common(5)
    print("Top 5 references used:")
    for ref, count in top_5:
        print(f"- {ref}: {count}")
    
    # Age summary
    # < 6 years: 2021-2026
    # 6-10 years: 2016-2020
    # > 10 years: before 2016
    age_groups = {
        "< 6 years old": 0,
        "6-10 years old": 0,
        "> 10 years old": 0
    }
    
    for year in years:
        age = current_year - year
        if age < 6:
            age_groups["< 6 years old"] += 1
        elif 6 <= age <= 10:
            age_groups["6-10 years old"] += 1
        else:
            age_groups["> 10 years old"] += 1
            
    total = len(years)
    print("\nSummary table with count and share of references by age:")
    print(f"{'Age Group':<20} | {'Count':<6} | {'Share (%)':<10}")
    print("-" * 43)
    for group, count in age_groups.items():
        share = (count / total * 100) if total > 0 else 0
        print(f"{group:<20} | {count:<6} | {share:<10.2f}")
    print(f"{'Total':<20} | {total:<6} | {'100.00':<10}")

def main():
    repo_root = Path('').parent
    thesis_path = repo_root / "thesis.md"
    if not thesis_path.exists():
        print(f"ERROR: File not found: {thesis_path}")
        raise SystemExit(1)

    analyze_references(thesis_path)

#========================== references to XML ==========================
import re
import xml.etree.ElementTree as ET
from pathlib import Path

INPUT_MD = Path("../references.md")      # adjust path if needed
OUTPUT_XML = Path("../documents/bibliography.xml")

# Word bibliography namespace
NS_B = "http://schemas.openxmlformats.org/officeDocument/2006/bibliography"
ET.register_namespace("b", NS_B)

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def split_authors(author_year: str):
    """
    Attempts to parse "Author1 & Author2, 2008" or "Author1, Author2, 2008"
    into (authors_list, year). Falls back gracefully.
    """
    s = normalize_whitespace(author_year)
    year = ""
    m = re.search(r"(\b19\d{2}\b|\b20\d{2}\b)", s)
    if m:
        year = m.group(1)
        # remove year and surrounding punctuation
        s = normalize_whitespace(re.sub(r"[,;]?\s*" + re.escape(year) + r"\s*$", "", s))
    # split authors on "&" or " and "
    parts = re.split(r"\s*(?:&| and )\s*", s)
    authors = [normalize_whitespace(p) for p in parts if normalize_whitespace(p)]
    return authors, year

def make_tag_from_row(author_year: str, title: str, url: str):
    base = normalize_whitespace(author_year + " " + title)
    base = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_")
    if not base:
        base = re.sub(r"[^A-Za-z0-9]+", "_", normalize_whitespace(url)).strip("_")
    return base[:48] or "Ref"

def parse_md_table(md_text: str):
    """
    Extracts rows from a GitHub-flavored markdown table with columns:
    | Author and year | URL | Title | File Name |
    Returns list of dicts.
    """
    lines = [l.rstrip("\n") for l in md_text.splitlines() if l.strip()]
    # Find header line containing the expected columns
    header_idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith("|") and "Author" in l and "URL" in l and "Title" in l:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("Could not find the references table header in references.md")

    # Next line should be the separator (---)
    start = header_idx + 2
    rows = []
    for l in lines[start:]:
        if not l.strip().startswith("|"):
            continue
        cols = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cols) < 3:
            continue
        # Handle both 3-col or 4-col variants; your file shows 4 columns
        author_year = cols[0]
        url = cols[1] if len(cols) >= 2 else ""
        title = cols[2] if len(cols) >= 3 else ""
        file_name = cols[3] if len(cols) >= 4 else ""
        if author_year.lower().startswith("---"):
            continue
        rows.append({
            "author_year": normalize_whitespace(author_year),
            "url": normalize_whitespace(url),
            "title": normalize_whitespace(title),
            "file_name": normalize_whitespace(file_name),
        })
    return rows

def generate_xml():
    if not INPUT_MD.exists():
        print(f"Skipping XML generation: {INPUT_MD} not found.")
        return

    md = INPUT_MD.read_text(encoding="utf-8")
    rows = parse_md_table(md)

    # Root element in b namespace
    sources = ET.Element(f"{{{NS_B}}}Sources")
    # SelectedStyle is usually NOT in a namespace
    sources.set("SelectedStyle", "\\APA.XSL") 

    for r in rows:
        author_year = r["author_year"]
        title = r["title"]
        url = r["url"]

        authors, year = split_authors(author_year)
        tag = make_tag_from_row(author_year, title, url)

        src = ET.SubElement(sources, f"{{{NS_B}}}Source")
        ET.SubElement(src, f"{{{NS_B}}}Tag").text = tag
        ET.SubElement(src, f"{{{NS_B}}}SourceType").text = "JournalArticle"

        # Author block
        author_el = ET.SubElement(src, f"{{{NS_B}}}Author")
        author_main = ET.SubElement(author_el, f"{{{NS_B}}}Author") # Word nesting: Author/Author/NameList
        name_list = ET.SubElement(author_main, f"{{{NS_B}}}NameList")

        for a in authors:
            tokens = a.split()
            last = tokens[-1] if tokens else a
            first = " ".join(tokens[:-1]) if len(tokens) > 1 else ""
            person = ET.SubElement(name_list, f"{{{NS_B}}}Person")
            ET.SubElement(person, f"{{{NS_B}}}Last").text = last
            if first:
                ET.SubElement(person, f"{{{NS_B}}}First").text = first

        if year:
            ET.SubElement(src, f"{{{NS_B}}}Year").text = year
        if title:
            ET.SubElement(src, f"{{{NS_B}}}Title").text = title
        if url:
            # For JournalArticle, Word often uses JournalName or URL
            # But JournalArticle specifically expects b:JournalName for the publication title.
            # We don't have JournalName in MD, so we put URL in b:URL
            ET.SubElement(src, f"{{{NS_B}}}URL").text = url
        
        ET.SubElement(src, f"{{{NS_B}}}Medium").text = "InternetSite"

    # Ensure output directory exists
    OUTPUT_XML.parent.mkdir(parents=True, exist_ok=True)
    
    tree = ET.ElementTree(sources)
    tree.write(OUTPUT_XML, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUTPUT_XML.resolve()} with {len(rows)} sources.")

if __name__ == "__main__":
    # If running functions.py directly, we do both word count/analysis AND xml generation
    main()
    generate_xml()