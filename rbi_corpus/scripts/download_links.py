import argparse
import json
import urllib.request
from pathlib import Path

from tqdm import tqdm


DEFAULT_OUTPUT_DIR = Path("../data/raw_pdfs")
DEFAULT_LINKS_FILE = DEFAULT_OUTPUT_DIR / "links.json"


def build_links_stub(links_file):
    links = [
        {
            "id": "nbfc_master_direction",
            "title": "NBFC Master Direction",
            "category": "nbfc",
            "date": "",
            "url": "",
        },
        {
            "id": "fair_practices_code",
            "title": "Fair Practices Code",
            "category": "nbfc",
            "date": "",
            "url": "",
        },
        {
            "id": "digital_lending",
            "title": "Digital Lending Guidelines",
            "category": "digital_lending",
            "date": "",
            "url": "",
        },
        {
            "id": "co_lending_model",
            "title": "Co-Lending Model Circular",
            "category": "co_lending",
            "date": "",
            "url": "",
        },
        {
            "id": "kyc_master_direction",
            "title": "KYC Master Direction",
            "category": "kyc",
            "date": "",
            "url": "",
        },
        {
            "id": "outsourcing_financial_services",
            "title": "Outsourcing of Financial Services",
            "category": "outsourcing",
            "date": "",
            "url": "",
        },
    ]

    links_file.parent.mkdir(parents=True, exist_ok=True)
    with open(links_file, "w", encoding="utf-8") as outfile:
        json.dump(links, outfile, ensure_ascii=False, indent=2)


def load_links(links_file):
    if not links_file.exists():
        build_links_stub(links_file)
        return []

    with open(links_file, "r", encoding="utf-8") as infile:
        return json.load(infile)


def resolve_output_path(output_dir, link):
    file_id = (link.get("id") or "document").strip()
    if not file_id.endswith(".pdf"):
        file_id = f"{file_id}.pdf"
    return output_dir / file_id


def download_file(url, output_path):
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request) as response:
        total = response.getheader("Content-Length")
        total = int(total) if total and total.isdigit() else None
        with open(output_path, "wb") as outfile, tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            desc=output_path.name,
        ) as progress:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                outfile.write(chunk)
                progress.update(len(chunk))


def download_pdfs(links_file, output_dir, force):
    links = load_links(links_file)
    if not links:
        print(
            f"Created {links_file}. Fill in RBI PDF URLs and re-run the script."
        )
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for link in links:
        url = (link.get("url") or "").strip()
        if not url:
            continue

        output_path = resolve_output_path(output_dir, link)
        if output_path.exists() and not force:
            continue

        download_file(url, output_path)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--links",
        type=Path,
        default=DEFAULT_LINKS_FILE,
        help="Path to links.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for downloaded PDFs",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing PDFs",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    download_pdfs(args.links, args.output_dir, args.force)
