def calculate_match_score(clause_text, keywords):
    clause_text = clause_text.lower()
    matched_keywords = [
        keyword for keyword in keywords
        if keyword.lower() in clause_text
    ]

    if not keywords:
        return 0.0, []

    score = len(matched_keywords) / len(keywords)
    return score, matched_keywords
