path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def draft_reply(review_text: str, sentiment: str, max_retries: int = 3) -> str:
    \"\"\"Generate a suggested seller reply to a customer review.\"\"\"
    client = _get_client()

    system_prompt = (
        \"You are a professional customer service assistant for an online seller. \"
        \"Given a customer review and its sentiment, write a short, warm, professional \"
        \"reply (2-4 sentences) the seller could send back to the customer. \"
        \"If the review is negative, acknowledge the issue and offer to make it right. \"
        \"If positive, thank them genuinely. Do not use markdown, just plain text.\"
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {\"role\": \"system\", \"content\": system_prompt},
                    {\"role\": \"user\", \"content\": f\"Sentiment: {sentiment}\\\\nReview: {review_text}\"},
                ],
                temperature=0.4,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = str(e)
            time.sleep(1)

    return f\"Could not generate reply: {last_error}\"
"""

if "def draft_reply" in content:
    print("draft_reply already exists - skipping.")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added draft_reply function.")
