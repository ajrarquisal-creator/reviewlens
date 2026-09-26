path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def generate_recommendations(theme_summary: dict, aspect_summary: dict, conflict_count: int, high_priority_count: int, max_retries: int = 3) -> list:
    \"\"\"Generate 3-5 concrete business recommendations based on aggregate analysis.\"\"\"
    client = _get_client()

    context_parts = []
    if theme_summary.get("top_complaints"):
        context_parts.append("Top complaints: " + "; ".join(theme_summary["top_complaints"]))
    if theme_summary.get("top_praises"):
        context_parts.append("Top praises: " + "; ".join(theme_summary["top_praises"]))
    if aspect_summary:
        aspect_lines = []
        for aspect, counts in aspect_summary.items():
            aspect_lines.append(f"{aspect}: {counts.get('negative', 0)} negative, {counts.get('positive', 0)} positive mentions")
        context_parts.append("Aspect breakdown: " + "; ".join(aspect_lines))
    context_parts.append(f"High priority reviews needing action: {high_priority_count}")
    context_parts.append(f"Sentiment/rating conflicts detected: {conflict_count}")

    context_text = chr(10).join(context_parts)

    system_prompt = (
        \"You are a business advisor for an online seller. Based on the review analysis \"
        \"summary provided, give 3-5 short, specific, actionable recommendations \"
        \"(1 sentence each) the seller could act on this week. Respond with ONLY a JSON \"
        \"object: {\\\"recommendations\\\": [list of short strings]}\"
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {\"role\": \"system\", \"content\": system_prompt},
                    {\"role\": \"user\", \"content\": context_text},
                ],
                temperature=0.4,
                max_tokens=400,
                response_format={\"type\": \"json_object\"},
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)
            return result.get("recommendations", [])
        except Exception as e:
            last_error = str(e)
            time.sleep(1)

    return [f"Could not generate recommendations: {last_error}"]
"""

if "def generate_recommendations" in content:
    print("already exists")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added generate_recommendations.")
