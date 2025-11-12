# extract_clauses.py
import re, json
from pypdf import PdfReader

def extract_clauses(pdf_path, output_json):
    reader = PdfReader(pdf_path)
    clause_re = re.compile(r'(^\d+\.\d+(?:\.\d+)*)')
    clauses = {}
    current = None
    buf = []

    for page in reader.pages:
        text = page.extract_text() or ""
        for line in text.split("\n"):
            m = clause_re.match(line.strip())
            if m:
                if current and buf:
                    clauses[current] = " ".join(buf).strip()
                current = m.group(1)
                buf = [line]
            elif current:
                buf.append(line)

    if current and buf:
        clauses[current] = " ".join(buf).strip()

    with open(output_json, "w") as f:
        json.dump(clauses, f, indent=2)
    print(f"✅ Extracted {len(clauses)} clauses from {pdf_path}")

# --- Run for each file you want ---
extract_clauses("data/AS3000.pdf", "data/as3000_clauses.json")
extract_clauses("data/QECM.pdf", "data/qecm_clauses.json")
extract_clauses("data/AS3017.pdf", "data/AS3017_clauses.json")
extract_clauses("data/AS3012.pdf", "data/AS3012_clauses.json")
extract_clauses("data/AS3010.pdf", "data/AS3010_clauses.json")



