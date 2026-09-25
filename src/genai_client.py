import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are a customer review analysis assistant.
Given a single product review, respond with ONLY a JSON object (no markdown, no extra text) with these exact fields:
{
  "sentiment": "positive" | "neutral" | "negative",
  "confidence": a number between 0 and 1,
  "keywords": a list of 3-5 short keyword strings from the review,
  "summary": a one-sentence summary of the review
}
"""


def _get_client() -> Groq:
    if not API_KEY:
        raise ValueError(
            "GROQ_API_KEY not found. Make sure it is set in your .env file."
        )
    return Groq(api_key=API_KEY)


def analyze_review(review_text: str, max_retries: int = 3) -> dict:
    """Send one review to Groq and return structured JSON analysis."""
    client = _get_client()

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": review_text},
                ],
                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)

            # Validate expected fields exist
            required_fields = ["sentiment", "confidence", "keywords", "summary"]
            missing = [f for f in required_fields if f not in result]
            if missing:
                raise ValueError(f"AI response missing fields: {missing}")

            return result

        except json.JSONDecodeError as e:
            last_error = f"Invalid JSON from API: {e}"
        except Exception as e:
            last_error = str(e)

            # Handle rate limiting with backoff
            if "rate_limit" in str(e).lower() or "429" in str(e):
                time.sleep(2 * attempt)
                continue

        # Small delay before retry on any failure
        time.sleep(1)

    # All retries failed — return a safe fallback
    return {
        "sentiment": "unknown",
        "confidence": 0.0,
        "keywords": [],
        "summary": f"Analysis failed: {last_error}",
        "error": True,
    }

def compute_priority(analysis: dict, star_rating: int) -> str:
    """
    Derive an action-priority flag for a seller triaging reviews.
    High: negative sentiment with high confidence, OR a low star rating
          that the AI also read as negative (confirmed real complaint).
    Medium: negative/neutral with lower confidence, or a rating/sentiment
             mismatch worth a human look.
    Low: everything else (confirmed positive, or low-confidence noise).
    """
    sentiment = analysis.get("sentiment", "unknown")
    confidence = analysis.get("confidence", 0.0)

    if analysis.get("error"):
        return "Medium"  # unresolved analysis deserves a human look

    if sentiment == "negative" and confidence >= 0.7:
        return "High"
    if sentiment == "negative" and star_rating <= 2:
        return "High"
    if sentiment in ("negative", "neutral") and confidence < 0.7:
        return "Medium"
    if sentiment == "positive" and star_rating <= 2:
        return "Medium"  # mismatch worth a glance
    return "Low"