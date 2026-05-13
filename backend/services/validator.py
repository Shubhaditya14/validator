from backend.services.matcher import calculate_match_score
from backend.services.scoring import map_severity


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
            "severity_score": map_severity(severity_label),
            "match_score": round(match_score, 2),
            "matched_keywords": matched_keywords,
            "version": rule.get("version", "1.0"),
            "description": rule.get("description", "")
        })

    return matches
