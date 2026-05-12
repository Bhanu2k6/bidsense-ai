import re

RISK_KEYWORDS = {
    "Missing Compliance": ["iso", "certification", "gst", "pan"],
    "Financial Risk": ["loss", "debt", "liability"],
    "Ambiguity Risk": ["may", "approximately", "subject to"],
    "Delivery Risk": ["delay", "no timeline", "tbd"],
}

def analyze_risk(vendor_text: str):
    risks = []
    score = 100

    text = vendor_text.lower()

    for risk, keywords in RISK_KEYWORDS.items():
        if not any(k in text for k in keywords):
            risks.append(risk)
            score -= 15

    score = max(score, 0)

    return {
        "risk_score": score,
        "risk_factors": risks if risks else ["Low Risk"]
    }
