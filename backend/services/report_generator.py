from backend.services.scoring import calculate_total_risk, classify_risk


def build_compliance_report(clause_text, predicted_category, matches):
    total_score = calculate_total_risk(matches)

    return {
        "clause": clause_text,
        "predicted_category": predicted_category,
        "overall_risk_score": total_score,
        "risk_level": classify_risk(total_score),
        "matches": matches
    }
