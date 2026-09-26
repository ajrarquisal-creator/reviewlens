path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def is_conflict(sentiment: str, star_rating) -> bool:
    \"\"\"Flags cases where AI sentiment and star rating disagree strongly.\"\"\"
    try:
        rating = float(star_rating)
    except (TypeError, ValueError):
        return False
    if sentiment == "negative" and rating >= 4:
        return True
    if sentiment == "positive" and rating <= 2:
        return True
    return False
"""

if "def is_conflict" in content:
    print("is_conflict already exists - skipping.")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added is_conflict function.")
