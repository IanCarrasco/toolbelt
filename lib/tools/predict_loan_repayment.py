import math
from typing import Any, Dict, List

def predict_loan_repayment(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict the probability (0-100) that an individual will repay a bank loan given demographic and financial features.
    Returns:
      - probability_percent: Predicted probability of repayment expressed 0-100.
      - probability_score: Normalized probability score between 0 and 1.
      - explanation: List of feature-level contributions ordered by absolute impact.
      - confidence: Model calibration estimate between 0 and 1.
      - model_version: Used model version string.
    Expected parameters:
      parameters: {
        "features": { ... feature values ... },
        "model_version": "optional model version string"
      }
    """
    features = parameters.get("features", {}) or {}
    model_version = parameters.get("model_version")
    if not isinstance(model_version, str) or not model_version:
        model_version = "v1.0-latest"

    # Model setup (deterministic, lightweight)
    intercept = -2.0
    age_coef = -0.01
    income_coef = 0.00015
    credit_score_coef = 0.012
    loan_amount_coef = -0.0009
    loan_term_coef = -0.0015

    # Track contributions per feature for explanation
    contributions: Dict[str, float] = {}

    def to_float(x: Any) -> float:
        try:
            return float(x)
        except (TypeError, ValueError):
            return 0.0

    logit = intercept

    # Numeric features
    if "age" in features and features["age"] is not None:
        val = to_float(features["age"])
        c = age_coef * val
        logit += c
        contributions["age"] = c
    else:
        contributions["age"] = 0.0

    if "income" in features and features["income"] is not None:
        val = to_float(features["income"])
        c = income_coef * val
        logit += c
        contributions["income"] = c
    else:
        contributions["income"] = 0.0

    if "credit_score" in features and features["credit_score"] is not None:
        val = to_float(features["credit_score"])
        c = credit_score_coef * val
        logit += c
        contributions["credit_score"] = c
    else:
        contributions["credit_score"] = 0.0

    if "loan_amount" in features and features["loan_amount"] is not None:
        val = to_float(features["loan_amount"])
        c = loan_amount_coef * val
        logit += c
        contributions["loan_amount"] = c
    else:
        contributions["loan_amount"] = 0.0

    if "loan_term_months" in features and features["loan_term_months"] is not None:
        val = to_float(features["loan_term_months"])
        c = loan_term_coef * val
        logit += c
        contributions["loan_term_months"] = c
    else:
        contributions["loan_term_months"] = 0.0

    # Categorical features (deterministic encoding for explanation)
    def category_contribution(feature_name: str, value: Any) -> float:
        s = str(value)
        h = sum(ord(ch) for ch in s)
        magnitude = (h % 60) * 0.03  # bounded magnitude
        sign = 1.0 if (h % 2 == 0) else -1.0
        bias = 0.0  # reserved for per-feature bias if needed
        return sign * magnitude + bias

    categorical_features = [
        "gender",
        "race",
        "employment_status",
        "education_level",
        "marital_status",
        "residence_status",
        "zipcode",
    ]
    for feat in categorical_features:
        val = features.get(feat)
        if val is not None:
            c = category_contribution(feat, val)
            logit += c
            contributions[feat] = c
        else:
            contributions[feat] = 0.0

    # Optional additional_features contribution (neutral/slight penalization if many extras)
    if isinstance(features.get("additional_features"), dict):
        count = len(features["additional_features"])
        c = -0.0005 * max(0, count)
        logit += c
        contributions["additional_features"] = c
    else:
        contributions["additional_features"] = 0.0

    # Probability calculation
    try:
        probability = 1.0 / (1.0 + math.exp(-logit))
    except OverflowError:
        probability = 1.0 if logit > 0 else 0.0

    probability_percent = max(0.0, min(100.0, probability * 100.0))
    probability_score = max(0.0, min(1.0, probability))

    # Explanation: sort by absolute contribution
    explanation: List[Dict[str, float]] = []
    for feat, contrib in contributions.items():
        explanation.append({"feature": feat, "contribution": float(contrib)})

    explanation.sort(key=lambda x: abs(x["contribution"]), reverse=True)

    # Confidence calibration (higher magnitude logit -> higher confidence)
    conf = 1.0 - math.exp(-abs(logit) / 4.0)  # yields value in (0, ~1]
    confidence = max(0.0, min(1.0, conf))

    return {
        "probability_percent": probability_percent,
        "probability_score": probability_score,
        "explanation": explanation,
        "confidence": confidence,
        "model_version": model_version,
    }