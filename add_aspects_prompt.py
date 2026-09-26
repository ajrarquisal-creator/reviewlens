path = "src/genai_client.py"
content = open(path, "r", encoding="utf-8").read()

old_prompt = """SYSTEM_PROMPT = \"\"\"You are a customer review analysis assistant.
Given a single product review, respond with ONLY a JSON object (no markdown, no extra text) with these exact fields:
{
  \"sentiment\": \"positive\" | \"neutral\" | \"negative\",
  \"confidence\": a number between 0 and 1,
  \"keywords\": a list of 3-5 short keyword strings from the review,
  \"summary\": a one-sentence summary of the review
}
\"\"\""""

new_prompt = """SYSTEM_PROMPT = \"\"\"You are a customer review analysis assistant.
Given a single product review, respond with ONLY a JSON object (no markdown, no extra text) with these exact fields:
{
  \"sentiment\": \"positive\" | \"neutral\" | \"negative\",
  \"confidence\": a number between 0 and 1,
  \"keywords\": a list of 3-5 short keyword strings from the review,
  \"summary\": a one-sentence summary of the review,
  \"aspects\": a list of 1-4 objects, each {\"aspect\": short product aspect like \\\"shipping\\\", \\\"taste\\\", \\\"price\\\", \\\"packaging\\\", \\\"quality\\\", \\\"customer service\\\", \"sentiment\": \"positive\" | \"neutral\" | \"negative\"}. Only include aspects actually discussed in the review.
}
\"\"\""""

if old_prompt in content:
    content = content.replace(old_prompt, new_prompt)
    print("Updated SYSTEM_PROMPT with aspects field.")
else:
    print("SYSTEM_PROMPT block not found - manual check needed.")

open(path, "w", encoding="utf-8").write(content)
