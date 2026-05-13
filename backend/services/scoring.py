SEVERITY_MAP = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}


def map_severity(severity_label):
    return SEVERITY_MAP.get(severity_label, 0)


def calculate_total_risk(matches):
    total = 0
    for match in matches:
        total += match["severity_score"] * match["match_score"]

    return round(total, 2)


def classify_risk(total_score):
    if total_score >= 5:
        return "HIGH RISK"
    if total_score >= 2:
        return "MEDIUM RISK"
    return "LOW RISK"
