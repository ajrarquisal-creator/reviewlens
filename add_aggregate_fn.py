path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def aggregate_aspects(results: list) -> dict:
    \"\"\"
    Combine per-review aspects into aspect-level counts and sentiment breakdown.
    results: list of analysis dicts (each may have an 'aspects' key).
    Returns: {aspect_name: {"positive": n, "neutral": n, "negative": n, "total": n}}
    \"\"\"
    summary = {}
    for r in results:
        for item in r.get("aspects", []) or []:
            aspect = item.get("aspect", "").strip().lower()
            sentiment = item.get("sentiment", "neutral")
            if not aspect:
                continue
            if aspect not in summary:
                summary[aspect] = {"positive": 0, "neutral": 0, "negative": 0, "total": 0}
            if sentiment not in summary[aspect]:
                sentiment = "neutral"
            summary[aspect][sentiment] += 1
            summary[aspect]["total"] += 1
    return summary
"""

if "def aggregate_aspects" in content:
    print("already exists")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added aggregate_aspects.")
