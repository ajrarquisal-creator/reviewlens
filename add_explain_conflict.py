path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def explain_conflict(sentiment: str, star_rating) -> str:
    \"\"\"Human-readable explanation for a sentiment/rating conflict.\"\"\"
    try:
        rating = float(star_rating)
    except (TypeError, ValueError):
        return "Sentiment and rating do not align."

    if sentiment == "negative" and rating >= 4:
        return f"Customer gave a high rating ({rating:.0f}\u2B50) but the review language reads as negative."
    if sentiment == "positive" and rating <= 2:
        return f"Customer gave a low rating ({rating:.0f}\u2B50) but the review language reads as positive."
    return "Sentiment and rating do not align."
"""

if "def explain_conflict" in content:
    print("already exists")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added explain_conflict.")
