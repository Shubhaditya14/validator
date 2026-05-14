# PRISM

PRISM is a Python backend pipeline for analyzing Indian MSME lending documents
and flagging clauses that may indicate predatory lending, weak disclosures, or
non-compliance with RBI digital lending expectations.

The project currently focuses on three backend responsibilities:

- Redacting Indian PII before legal text enters the ML or rule-analysis stages.
- Matching predicted legal clauses against RBI-inspired compliance rules.
- Producing risk scores and compliance report dictionaries for downstream use.

## Project Layout

```text
.
├── backend/
│   ├── rules/
│   │   └── rbi_rules.json
│   └── services/
│       ├── matcher.py
│       ├── pii_scrubber.py
│       ├── report_generator.py
│       ├── scoring.py
│       └── validator.py
├── rbi_corpus/
│   ├── data/
│   ├── scripts/
│   └── README.md
├── requirements.txt
└── validator.py
```

## Pipeline Overview

```text
Raw document text
  -> PII scrubbing
  -> Clause segmentation / ML classification
  -> Rule validation
  -> Risk scoring
  -> Compliance report
```

`backend/services/pii_scrubber.py` is designed to run before clause
segmentation so sensitive borrower details are removed before the text is used
by the ML pipeline or stored in analysis artifacts.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The PII scrubber itself uses only the Python standard library: `re` and `json`.
The dependencies in `requirements.txt` are for RBI corpus PDF extraction.

## PII Scrubber

Import:

```python
from backend.services.pii_scrubber import scrub_pii, scrub_pii_with_log
```

Basic usage:

```python
text = "Borrower PAN ABCDE1234F and phone 9876543210"

print(scrub_pii(text))
# Borrower PAN [PAN_REDACTED] and phone [PHONE_REDACTED]
```

Audit usage:

```python
result = scrub_pii_with_log(text)

print(result["scrubbed_text"])
print(result["redactions"])
```

Return shape:

```python
{
    "scrubbed_text": "Borrower PAN [PAN_REDACTED] and phone [PHONE_REDACTED]",
    "redactions": [
        {"type": "PAN", "original": "ABCDE1234F", "position": 13},
        {"type": "PHONE", "original": "9876543210", "position": 33},
    ],
}
```

Supported redactions:

| PII type | Detection | Placeholder |
| --- | --- | --- |
| Aadhaar | 12 digits, optional spaces in groups of 4 | `[AADHAAR_REDACTED]` |
| PAN | 5 uppercase letters, 4 digits, 1 uppercase letter | `[PAN_REDACTED]` |
| Bank account | 9 to 18 digit sequence | `[BANK_ACCOUNT_REDACTED]` |
| IFSC | 4 letters, `0`, 6 alphanumeric chars | `[IFSC_REDACTED]` |
| Phone | Indian mobile number starting with 6, 7, 8, or 9 | `[PHONE_REDACTED]` |
| Email | Standard email pattern | `[EMAIL_REDACTED]` |
| Address line | Lines containing address keywords | `[ADDRESS_REDACTED]` |

Address keywords currently include `Plot`, `Flat`, `Door No`, `Survey No`,
`Village`, `Taluk`, `District`, and `Pin`.

The scrubber preserves non-PII text exactly, including whitespace and newlines.
When numeric patterns overlap, redactions are applied in module priority order.
For example, a bare 12-digit number is treated as Aadhaar before the broader
bank-account rule.

Run the built-in demo:

```bash
python3 backend/services/pii_scrubber.py
```

The demo prints three before/after examples and a JSON audit log covering all
supported PII categories.

## Rule Validation

Rules live in:

```text
backend/rules/rbi_rules.json
```

Each rule includes:

- `id`
- `title`
- `category`
- `description`
- `pattern_keywords`
- `severity`
- `threshold`
- `enabled`

Validate a clause:

```python
import json

from backend.services.validator import validate_clause
from backend.services.report_generator import build_compliance_report

with open("backend/rules/rbi_rules.json", "r", encoding="utf-8") as rules_file:
    rules = json.load(rules_file)

clause = "The lender may revise the interest rate without prior notice."
category = "unilateral_rate_change"

matches = validate_clause(clause, category, rules)
report = build_compliance_report(clause, category, matches)

print(report)
```

## Risk Scoring

Severity values are mapped in `backend/services/scoring.py`:

| Severity | Score |
| --- | --- |
| LOW | 1 |
| MEDIUM | 2 |
| HIGH | 3 |
| CRITICAL | 4 |

Total risk is calculated as:

```text
sum(severity_score * match_score)
```

Risk classification:

| Total score | Risk level |
| --- | --- |
| `>= 5` | `HIGH RISK` |
| `>= 2` and `< 5` | `MEDIUM RISK` |
| `< 2` | `LOW RISK` |

## RBI Corpus Pipeline

The `rbi_corpus/` directory contains scripts for downloading, extracting,
cleaning, and processing RBI PDF circulars into JSONL data.

See:

```text
rbi_corpus/README.md
```

Typical flow:

```bash
cd rbi_corpus
python scripts/download_links.py
python scripts/extract_text.py
python scripts/build_jsonl.py
```

## Verification

Compile backend modules:

```bash
python3 -m py_compile backend/services/pii_scrubber.py
python3 -m py_compile backend/services/matcher.py
python3 -m py_compile backend/services/scoring.py
python3 -m py_compile backend/services/validator.py
python3 -m py_compile backend/services/report_generator.py
```

Run the PII scrubber demo:

```bash
python3 backend/services/pii_scrubber.py
```

Run a quick assertion check:

```bash
python3 -c '
from backend.services.pii_scrubber import scrub_pii, scrub_pii_with_log

text = """Aadhaar 1234 5678 9012
PAN ABCDE1234F
Account 123456789012345 IFSC SBIN0123456
Phone 9876543210 Email test@example.com
Flat 1, Plot 2, District Pune, Pin 411001
Keep this line."""

result = scrub_pii_with_log(text)
scrubbed = result["scrubbed_text"]

for placeholder in [
    "[AADHAAR_REDACTED]",
    "[PAN_REDACTED]",
    "[BANK_ACCOUNT_REDACTED]",
    "[IFSC_REDACTED]",
    "[PHONE_REDACTED]",
    "[EMAIL_REDACTED]",
    "[ADDRESS_REDACTED]",
]:
    assert placeholder in scrubbed, placeholder

assert "Keep this line." in scrubbed
assert scrub_pii(text) == scrubbed
assert len(result["redactions"]) == 7
assert all(set(item) == {"type", "original", "position"} for item in result["redactions"])

print("PII scrubber assertions passed")
'
```

## Current Status

This repository is currently a backend library and corpus-preparation workspace.
It does not yet include a packaged CLI, HTTP API, database layer, or full test
suite. The service modules can be imported directly by a future API, batch job,
or notebook pipeline.

## Notes

- PII scrubbing is regex-based and should be treated as a preprocessing guard,
  not a complete privacy compliance system.
- Address detection redacts full lines when common Indian address keywords are
  present.
- Rule validation depends on an upstream classifier supplying the predicted
  clause category.
- Existing RBI rules are keyword/threshold based and should be reviewed before
  production use.

