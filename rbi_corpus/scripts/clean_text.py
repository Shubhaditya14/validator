import re


def clean_text(text):
    # Normalize whitespace
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\t+", " ", text)

    # Remove page numbers like "Page 12 of 45"
    text = re.sub(r"\bPage\s+\d+\s+of\s+\d+\b", "", text, flags=re.IGNORECASE)

    # Remove repeated header/footer artifacts often seen in RBI PDFs
    text = re.sub(r"Reserve Bank of India", "", text, flags=re.IGNORECASE)
    text = re.sub(r"https?://\S+", "", text)

    # Collapse multiple spaces and newlines
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
