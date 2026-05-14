"""PII scrubbing for PRISM legal document analysis.

This module runs before clause segmentation in the ML pipeline so sensitive
Indian identifiers and address details are removed before downstream predatory
lending detection for MSME documents.
"""

import json
import re


PATTERNS = [
    (
        "AADHAAR",
        "[AADHAAR_REDACTED]",
        re.compile(r"(?<!\d)(?:\d{4}[ ]?\d{4}[ ]?\d{4})(?!\d)"),
    ),
    (
        "PAN",
        "[PAN_REDACTED]",
        re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    ),
    (
        "IFSC",
        "[IFSC_REDACTED]",
        re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
    ),
    (
        "EMAIL",
        "[EMAIL_REDACTED]",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ),
    (
        "PHONE",
        "[PHONE_REDACTED]",
        re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)"),
    ),
    (
        "BANK_ACCOUNT",
        "[BANK_ACCOUNT_REDACTED]",
        re.compile(r"(?<!\d)\d{9,18}(?!\d)"),
    ),
    (
        "ADDRESS",
        "[ADDRESS_REDACTED]",
        re.compile(
            r"^.*\b(?:Plot|Flat|Door No|Survey No|Village|Taluk|District|Pin)\b.*$",
            re.IGNORECASE | re.MULTILINE,
        ),
    ),
]


def _collect_redactions(text):
    redactions = []
    occupied = []

    for pii_type, placeholder, pattern in PATTERNS:
        for match in pattern.finditer(text):
            start, end = match.span()
            if any(start < used_end and end > used_start for used_start, used_end in occupied):
                continue

            redactions.append({
                "type": pii_type,
                "original": match.group(0),
                "position": start,
                "placeholder": placeholder,
                "end": end,
            })
            occupied.append((start, end))

    return sorted(redactions, key=lambda item: item["position"])


def scrub_pii(text: str) -> str:
    """Return text with Indian PII replaced by labeled placeholders."""
    return scrub_pii_with_log(text)["scrubbed_text"]


def scrub_pii_with_log(text: str) -> dict:
    """Return scrubbed text plus an audit log of removed PII."""
    redactions = _collect_redactions(text)
    scrubbed_parts = []
    cursor = 0

    for redaction in redactions:
        start = redaction["position"]
        end = redaction["end"]
        scrubbed_parts.append(text[cursor:start])
        scrubbed_parts.append(redaction["placeholder"])
        cursor = end

    scrubbed_parts.append(text[cursor:])

    audit_log = []
    for redaction in redactions:
        audit_log.append({
            "type": redaction["type"],
            "original": redaction["original"],
            "position": redaction["position"],
        })

    return {
        "scrubbed_text": "".join(scrubbed_parts),
        "redactions": audit_log,
    }


if __name__ == "__main__":
    samples = [
        (
            "Borrower Aadhaar: 1234 5678 9012\n"
            "PAN: ABCDE1234F\n"
            "Contact: 9876543210\n"
            "Email: owner@example.co.in"
        ),
        (
            "Repayment account 123456789012345 with IFSC HDFC0123456.\n"
            "Alternate account: 987654321\n"
            "The borrower accepts the processing fee clause."
        ),
        (
            "Collateral address:\n"
            "Flat 12, Plot 44, Village Nelamangala, District Bengaluru, Pin 562123\n"
            "Survey No 18/2, Taluk Doddaballapura\n"
            "Non-PII clause text stays exactly as written."
        ),
    ]

    for index, sample in enumerate(samples, start=1):
        result = scrub_pii_with_log(sample)
        print(f"--- Sample {index} Before ---")
        print(sample)
        print(f"--- Sample {index} After ---")
        print(result["scrubbed_text"])
        print("--- Redactions ---")
        print(json.dumps(result["redactions"], indent=2))
