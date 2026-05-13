import argparse
import json
from pathlib import Path


INPUT_FILE = Path("../data/extracted/rbi_circulars.jsonl")
OUTPUT_FILE = Path("../data/processed/rbi_circulars_processed.jsonl")


def chunk_text(text, chunk_size):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def build_processed(chunk, chunk_size):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, open(
        OUTPUT_FILE, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)

            if not chunk:
                outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
                continue

            text = record.get("text", "")
            chunks = chunk_text(text, chunk_size)

            for idx, chunk_text_value in enumerate(chunks, start=1):
                chunk_record = {
                    "chunk_id": f"{record.get('id', 'doc')}_{idx}",
                    "id": record.get("id", ""),
                    "title": record.get("title", ""),
                    "category": record.get("category", ""),
                    "date": record.get("date", ""),
                    "source": record.get("source", ""),
                    "text": chunk_text_value,
                }
                outfile.write(json.dumps(chunk_record, ensure_ascii=False) + "\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk", action="store_true", help="Enable chunking")
    parser.add_argument("--chunk-size", type=int, default=1000)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_processed(args.chunk, args.chunk_size)
