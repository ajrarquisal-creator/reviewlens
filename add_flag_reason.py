path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def get_flag_reason(analysis: dict, star_rating, priority: str) -> dict:
    \"\"\"
    Explain why a review was flagged and suggest a next action.
    Returns {"reason": str, "action": str}
    \"\"\"
    sentiment = analysis.get("sentiment", "unknown")
    confidence = analysis.get("confidence", 0.0)

    try:
        rating = float(star_rating)
    except (TypeError, ValueError):
        rating = None

    if priority != "High":
        return {"reason": "Standard review, no urgent action needed.", "action": "Monitor"}

    if sentiment == "negative" and confidence >= 0.7:
        reason = f"Strongly negative sentiment ({confidence:.0%} confidence)."
        action = "Respond promptly and offer a resolution."
    elif sentiment == "negative" and rating is not None and rating <= 2:
        reason = f"Negative review paired with a low {rating:.0f}\u2B50 rating."
        action = "Investigate the issue and reach out to the customer."
    elif rating is not None and sentiment == "positive" and rating <= 2:
        reason = f"AI reads positive tone but customer gave only {rating:.0f}\u2B50 - possible mismatch."
        action = "Review manually to confirm true sentiment."
    else:
        reason = "Flagged as high priority based on combined signals."
        action = "Review manually."

    return {"reason": reason, "action": action}
"""

if "def get_flag_reason" in content:
    print("already exists")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added get_flag_reason.")
