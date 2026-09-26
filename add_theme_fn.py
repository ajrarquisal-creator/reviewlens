path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def summarize_themes(review_summaries: list, max_retries: int = 3) -> dict:
    \"\"\"Given a list of review summaries, extract top recurring themes.\"\"\"
    client = _get_client()

    combined_text = chr(10).join(f"- {s}" for s in review_summaries)

    system_prompt = (
        \"You are a customer feedback analyst. You will be given a list of review \"
        \"summaries. Respond with ONLY a JSON object (no markdown) with these fields: \"
        \"{\\\"top_complaints\\\": [list of up to 3 short strings], \"
        \"\\\"top_praises\\\": [list of up to 3 short strings], \"
        \"\\\"overall_takeaway\\\": one sentence string}\"
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {\"role\": \"system\", \"content\": system_prompt},
                    {\"role\": \"user\", \"content\": combined_text},
                ],
                temperature=0.3,
                max_tokens=400,
                response_format={\"type\": \"json_object\"},
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)
            return result
        except Exception as e:
            last_error = str(e)
            time.sleep(1)

    return {
        \"top_complaints\": [],
        \"top_praises\": [],
        \"overall_takeaway\": f\"Could not generate summary: {last_error}\",
    }
"""

if "def summarize_themes" in content:
    print("already exists")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added summarize_themes.")
