# RBI Corpus Pipeline

Mini pipeline to build a JSONL corpus from RBI circular PDFs.

## Layout

```
rbi_corpus/
  data/
    raw_pdfs/
    extracted/
    processed/
  scripts/
    download_links.py
    extract_text.py
    clean_text.py
    build_jsonl.py
  requirements.txt
  README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

## Step 1: Add PDFs

Download RBI circular PDFs and put them in:

```
data/raw_pdfs/
```

Suggested starter set:

- NBFC Master Direction
- Fair Practices Code
- Digital Lending Guidelines
- Co-Lending Model Circular
- KYC Master Direction
- Outsourcing of Financial Services

The repository includes a prefilled `data/raw_pdfs/links.json` with RBI PDF
links for the starter set. If you want to regenerate the stub, run:

```bash
python scripts/download_links.py --links data/raw_pdfs/links.json --force
```

To download automatically using the provided URLs:

```bash
python scripts/download_links.py
```

## Step 2: Extract + Clean

```bash
python scripts/extract_text.py
```

Output:

```
data/extracted/rbi_circulars.jsonl
```

Each line is a JSON object like:

```json
{"id":"digital_lending","title":"Reserve Bank of India (Digital Lending) Directions, 2025","category":"digital_lending","date":"2025-05-08","source":"data/raw_pdfs/digital_lending.pdf","text":"..."}
```

## Step 3: Build Processed JSONL (Optional Chunking)

```bash
python scripts/build_jsonl.py
```

With chunking:

```bash
python scripts/build_jsonl.py --chunk --chunk-size 1000
```

Output:

```
data/processed/rbi_circulars_processed.jsonl
```

## Notes

- Extraction uses `pdfplumber` first and falls back to `PyMuPDF` if the text
  looks empty or very short.
- Cleaning removes common header/footer artifacts, page numbers, and repeated
  whitespace.
- Keep V1 simple: download PDFs, extract text, clean, and write JSONL.
