"""
explainer.py - LLM-powered plain-language explanations

Setup (adjust to your needs):
    pip install google-genai
    Get a free API key at: aistudio.google.com -> Get API key

    Add to .env:
    GEMINI_API_KEY=your_key_here
"""

import os

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            from google import genai
            key = os.environ.get("GEMINI_API_KEY", "")
            if not key:
                _client = "unavailable"
            else:
                _client = genai.Client(api_key=key)
        except ImportError:
            _client = "unavailable"
    return _client


def _build_prompt(scan_type: str, subject: str, risk_level: str, probability: float, flags: list) -> str:
    flag_lines = []
    for f in flags:
        if isinstance(f, str):
            flag_lines.append(f"- {f}")
        elif isinstance(f, dict):
            cat = f.get("category", "")
            det = f.get("detail", "")
            flag_lines.append(f"- {cat}: {det}" if det else f"- {cat}")

    flags_text = "\n".join(flag_lines) if flag_lines else "- No specific flags raised"

    type_labels = {"url": "URL / link", "email": "email", "phone": "phone number"}
    type_label = type_labels.get(scan_type, "item")

    risk_descriptions = {
        "high":   "very likely to be a scam or phishing attack",
        "medium": "showing some suspicious characteristics worth being cautious about",
        "low":    "not showing obvious signs of fraud",
    }
    risk_desc = risk_descriptions.get(risk_level, risk_level)

    return f"""You are a cybersecurity assistant helping vulnerable people - elderly citizens, refugees, and people with low digital literacy - understand whether something is a scam.

A phishing detector analysed this {type_label}: "{subject}"

Result: {risk_level.upper()} RISK ({probability:.0f}% phishing probability) - {risk_desc}.

Signals detected:
{flags_text}

Write 2-4 sentences for someone with no technical background:
- Explain WHY this is suspicious (or safe) using the signals above
- If high/medium risk: tell them clearly what NOT to do
- If low risk: remind them to stay alert
- Plain language, no jargon, no bullet points
- Do not start with "I"

Write only the explanation, nothing else."""


def explain(scan_type: str, subject: str, risk_level: str, probability: float,
            flags: list, fallback_explanation: str) -> tuple:
    client = _get_client()

    if client == "unavailable":
        return fallback_explanation, False

    try:
        from google import genai
        prompt = _build_prompt(scan_type, subject, risk_level, probability, flags)
        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=prompt,
        )
        text = response.text.strip()

        if len(text) < 30:
            return fallback_explanation, False

        return text, True

    except Exception:
        return fallback_explanation, False
