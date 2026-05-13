SEVERITY_MAP = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}


def calculate_match_score(clause_text, keywords):
    clause_text = clause_text.lower()
    matched_keywords = []

    for keyword in keywords:
        if keyword.lower() in clause_text:
            matched_keywords.append(keyword)

    if not keywords:
        return 0.0, []

    score = len(matched_keywords) / len(keywords)
    return score, matched_keywords


def validate_clause(clause_text, predicted_category, rules):
    matches = []

    for rule in rules:
        if not rule.get("enabled", True):
            continue

        if rule.get("category") != predicted_category:
            continue

        match_score, matched_keywords = calculate_match_score(
            clause_text,
            rule.get("pattern_keywords", [])
        )

        threshold = rule.get("threshold", 0.2)
        if match_score < threshold:
            continue

        severity_label = rule.get("severity", "")

        matches.append({
            "rule_id": rule.get("id"),
            "title": rule.get("title"),
            "severity": severity_label,
            "severity_score": SEVERITY_MAP.get(severity_label, 0),
            "match_score": round(match_score, 2),
            "matched_keywords": matched_keywords,
            "version": rule.get("version", "1.0"),
            "description": rule.get("description", "")
        })

    return matches


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
