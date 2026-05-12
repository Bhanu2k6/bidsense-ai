# services/analysis_engine.py

import re
from typing import Dict, Any, Optional, List

from fastapi import UploadFile
from .document_ai import extract_text_from_pdf

# 🔥 Fraud detection imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# ⚠️ Risk Management Rules (Business + Compliance)
# =========================================================
RISK_RULES = {
    "Missing GST": lambda f: not f.get("has_gst"),

    "Missing ISO Certification": lambda f: not f.get("has_iso"),

    "Insufficient Experience": lambda f, r: (
        f.get("experience_years") is None or
        r.get("required_experience_years") is not None and
        f.get("experience_years", 0) < r.get("required_experience_years", 0)
    ),

    "Delivery Risk": lambda f, r: (
        f.get("delivery_days") is None or
        r.get("max_delivery_days") is not None and
        f.get("delivery_days", 9999) > r.get("max_delivery_days", 9999)
    ),
}


# =========================================================
# 🤖 MAIN ORCHESTRATOR (Decision Agent)
# =========================================================
async def analyze(
    tender: UploadFile,
    vendors: Dict[str, UploadFile]
) -> Dict[str, Any]:

    # ---------------------------------------------------------
    # 1️⃣ Document Agent — Extract tender + vendor text
    # ---------------------------------------------------------
    tender_text = await extract_text_from_pdf(tender)

    requirements = _parse_tender_requirements(tender_text)

    vendor_data: Dict[str, Dict[str, Any]] = {}

    for key, file in vendors.items():

        text = await extract_text_from_pdf(file)

        features = _parse_vendor_features(text)

        vendor_data[key] = {
            "filename": file.filename,
            "text": text,
            "features": features,
        }

    # ---------------------------------------------------------
    # 2️⃣ Financial Agent — Price normalization
    # ---------------------------------------------------------
    prices = [
        v["features"]["price"]
        for v in vendor_data.values()
        if v["features"]["price"] is not None
    ]

    min_price = min(prices) if prices else None
    max_price = max(prices) if prices else None

    tech_weight = requirements.get("technical_weight", 0.6)
    fin_weight = requirements.get("financial_weight", 0.4)
    risk_weight = 0.2

    # ---------------------------------------------------------
    # 3️⃣ Compliance + Financial + Risk Scoring Agent
    # ---------------------------------------------------------
    match_list: List[Dict[str, Any]] = []

    for key, data in vendor_data.items():

        f = data["features"]

        tech_score = _compute_technical_score(f, requirements)

        fin_score = _compute_financial_score(
            f,
            min_price,
            max_price
        )

        risk = _analyze_risk(f, requirements)

        total_score = (
            tech_weight * 0.8 * tech_score +
            fin_weight * 0.8 * fin_score +
            risk_weight * risk["risk_score"]
        )

        match_list.append({
            "vendor_id": key,
            "vendor_name": data["filename"],
            "technical_score": round(tech_score, 2),
            "financial_score": round(fin_score, 2),
            "risk_score": risk["risk_score"],
            "risk_factors": risk["risk_factors"],
            "total_score": round(total_score, 2),
        })

    # ---------------------------------------------------------
    # 4️⃣ Decision Agent — Rank vendors
    # ---------------------------------------------------------
    match_list_sorted = sorted(
        match_list,
        key=lambda x: x["total_score"],
        reverse=True
    )

    best_vendor = match_list_sorted[0] if match_list_sorted else None

    winner_reasons = (
        _explain_winner(best_vendor)
        if best_vendor else []
    )

    # ---------------------------------------------------------
    # 5️⃣ Fraud Agent — Copy / Similarity Detection
    # ---------------------------------------------------------
    vendor_texts = {
        key: data["text"]
        for key, data in vendor_data.items()
    }

    fraud_flags = _detect_fraud(vendor_texts)

    # ---------------------------------------------------------
    # 6️⃣ FINAL RESPONSE
    # ---------------------------------------------------------
    return {
        "tender_name": tender.filename,

        "requirements": requirements,

        "winner": {
            "vendor_name": best_vendor["vendor_name"],
            "total_score": best_vendor["total_score"],
            "reasons": winner_reasons
        } if best_vendor else None,

        "matches": match_list_sorted,

        "fraud_flags": fraud_flags
    }


# =========================================================
# 🧩 HELPER / AGENT FUNCTIONS
# =========================================================

def _parse_tender_requirements(text: str) -> Dict[str, Any]:

    lower = text.lower()

    req_exp = _extract_first_int(r"(\d+)\s+years", lower)

    max_delivery = _extract_first_int(r"(\d+)\s+days", lower)

    tech_weight = _extract_first_int(
        r"technical:\s*(\d+)%",
        lower
    )

    fin_weight = _extract_first_int(
        r"financial:\s*(\d+)%",
        lower
    )

    if tech_weight is not None and fin_weight is not None:

        tech_weight_f = tech_weight / 100.0
        fin_weight_f = fin_weight / 100.0

    else:

        tech_weight_f = 0.6
        fin_weight_f = 0.4

    return {
        "required_experience_years": req_exp,
        "max_delivery_days": max_delivery,
        "technical_weight": tech_weight_f,
        "financial_weight": fin_weight_f,
    }


def _parse_vendor_features(text: str) -> Dict[str, Any]:

    lower = text.lower()

    has_gst = "gst" in lower
    has_iso = "iso" in lower

    experience_years = _extract_first_int(
        r"(\d+)\s+years",
        lower
    )

    delivery_days = _extract_first_int(
        r"(\d+)\s+days",
        lower
    )

    price_match = re.search(r"(\d[\d,]{3,})", text)

    price = (
        int(price_match.group(1).replace(",", ""))
        if price_match else None
    )

    return {
        "has_gst": has_gst,
        "has_iso": has_iso,
        "experience_years": experience_years,
        "delivery_days": delivery_days,
        "price": price,
    }


def _compute_technical_score(
    features: Dict[str, Any],
    req: Dict[str, Any]
) -> float:

    score = 0.0

    if features.get("has_gst"):
        score += 20

    if features.get("has_iso"):
        score += 20

    if (
        req.get("required_experience_years") is not None and
        features.get("experience_years") is not None and
        features["experience_years"] >= req["required_experience_years"]
    ):
        score += 30

    if (
        req.get("max_delivery_days") is not None and
        features.get("delivery_days") is not None and
        features["delivery_days"] <= req["max_delivery_days"]
    ):
        score += 30

    return score


def _compute_financial_score(
    features: Dict[str, Any],
    min_price: Optional[int],
    max_price: Optional[int]
) -> float:

    price = features.get("price")

    if (
        price is None or
        min_price is None or
        max_price is None
    ):
        return 0.0

    if min_price == max_price:
        return 100.0

    ratio = (
        (max_price - price) /
        (max_price - min_price)
    )

    return 50.0 + ratio * 50.0


def _extract_first_int(
    pattern: str,
    text: str
) -> Optional[int]:

    m = re.search(pattern, text)

    return int(m.group(1)) if m else None


# =========================================================
# ⚠️ Risk Agent — Business & Compliance Risk
# =========================================================
def _analyze_risk(
    features: Dict[str, Any],
    requirements: Dict[str, Any]
):

    risks = []
    score = 100.0

    for risk, rule in RISK_RULES.items():

        try:
            violated = rule(features, requirements)

        except TypeError:
            violated = rule(features)

        if violated:

            risks.append(risk)

            # Weighted Risk Penalties
            if risk == "Missing GST":
                score -= 25

            elif risk == "Missing ISO Certification":
                score -= 20

            elif risk == "Insufficient Experience":
                score -= 20

            elif risk == "Delivery Risk":
                score -= 15

    return {
        "risk_score": max(round(score, 2), 0),
        "risk_factors": risks if risks else ["Low Risk"]
    }


# =========================================================
# 🏆 Winner Explanation Agent
# =========================================================
def _explain_winner(
    winner: Dict[str, Any]
) -> List[str]:

    reasons = []

    if winner["technical_score"] >= 60:
        reasons.append("Strong technical compliance")

    if winner["financial_score"] >= 70:
        reasons.append("Competitive pricing")

    if winner["risk_score"] >= 80:
        reasons.append("Low risk profile")

    reasons.append(
        "Highest overall score among all vendors"
    )

    return reasons


# =========================================================
# 🚨 Fraud Agent — Copy / Similarity Detection
# =========================================================
def _detect_fraud(
    vendor_texts: Dict[str, str],
    threshold: float = 0.8
):

    if len(vendor_texts) < 2:
        return []

    ids = list(vendor_texts.keys())
    texts = list(vendor_texts.values())

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf = vectorizer.fit_transform(texts)

    sim_matrix = cosine_similarity(tfidf)

    frauds = []

    for i in range(len(ids)):

        for j in range(i + 1, len(ids)):

            score = sim_matrix[i][j]

            if score >= threshold:

                frauds.append({
                    "vendor_1": ids[i],
                    "vendor_2": ids[j],
                    "similarity": round(float(score), 2),
                    "risk": "POSSIBLE_COPY_BID"
                })

    return frauds