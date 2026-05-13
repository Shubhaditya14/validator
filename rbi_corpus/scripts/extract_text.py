import json
from pathlib import Path

import pdfplumber
import fitz
from tqdm import tqdm

from clean_text import clean_text


RAW_DIR = Path("../data/raw_pdfs")
OUTPUT_FILE = Path("../data/extracted/rbi_circulars.jsonl")
LINKS_FILE = Path("../data/raw_pdfs/links.json")


def extract_pdf_text(pdf_path):
    text_chunks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)

    return "\n".join(text_chunks)


def extract_with_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text


def load_metadata():
    if not LINKS_FILE.exists():
        return {}

    with open(LINKS_FILE, "r", encoding="utf-8") as infile:
        entries = json.load(infile)

    return {entry.get("id"): entry for entry in entries}


def build_dataset():
    pdf_files = list(RAW_DIR.glob("*.pdf"))
    metadata = load_metadata()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for pdf_file in tqdm(pdf_files):
            extracted_text = extract_pdf_text(pdf_file)

            if len(extracted_text.strip()) < 100:
                extracted_text = extract_with_fitz(pdf_file)

            cleaned_text = clean_text(extracted_text)

            meta = metadata.get(pdf_file.stem, {})

            entry = {
                "id": pdf_file.stem,
                "title": meta.get("title", ""),
                "category": meta.get("category", ""),
                "date": meta.get("date", ""),
                "source": str(pdf_file),
                "text": cleaned_text,
            }

            outfile.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    build_dataset()
