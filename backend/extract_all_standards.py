import re, json, os
from pypdf import PdfReader

def extract_clauses_from_pdf(pdf_path):
    clause_pattern = re.compile(r'(^\d+\.\d+(?:\.\d+)*)')
    reader = PdfReader(pdf_path)
    clauses = {}
    current = None
    buffer = []

    for page in reader.pages:
        text = page.extract_text() or ""
        for line in text.split("\n"):
            match = clause_pattern.match(line.strip())
            if match:
                if current and buffer:
                    clauses[current] = " ".join(buffer).strip()
                current = match.group(1)
                buffer = [line]
            elif current:
                buffer.append(line)

    if current and buffer:
        clauses[current] = " ".join(buffer).strip()

    return clauses

def extract_all_pdfs(data_folder="data"):
    pdf_files = [f for f in os.listdir(data_folder) if f.lower().endswith(".pdf")]
    for pdf in pdf_files:
        name = os.path.splitext(pdf)[0]
        print(f"📘 Extracting {name}...")
        clauses = extract_clauses_from_pdf(os.path.join(data_folder, pdf))
        output_file = os.path.join(data_folder, f"{name}.json")
        with open(output_file, "w") as f:
            json.dump(clauses, f, indent=2)
        print(f"✅ Saved {len(clauses)} clauses to {output_file}")

if __name__ == "__main__":
    extract_all_pdfs("data")
