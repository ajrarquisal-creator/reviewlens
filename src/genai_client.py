import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()


def _get_api_key():
    """Check .env / OS env first (local dev), fall back to Streamlit secrets (cloud)."""
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    if st is not None:
        try:
            return st.secrets.get("GROQ_API_KEY")
        except Exception:
            return None
    return None


API_KEY = _get_api_key()
MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are a customer review analysis assistant.
Given a single product review, respond with ONLY a JSON object (no markdown, no extra text) with these exact fields:
{
  "sentiment": "positive" | "neutral" | "negative",
  "confidence": a number between 0 and 1,
  "keywords": a list of 3-5 short keyword strings from the review,
  "summary": a one-sentence summary of the review,
  "aspects": a list of 1-4 objects, each {"aspect": short product aspect like \"shipping\", \"taste\", \"price\", \"packaging\", \"quality\", \"customer service\", "sentiment": "positive" | "neutral" | "negative"}. Only include aspects actually discussed in the review.
}
"""


def _get_client() -> Groq:
    key = _get_api_key()
    if not key:
        raise ValueError(
            "GROQ_API_KEY not found. Set it in your .env file locally, "
            "or in Streamlit Cloud's Secrets manager when deployed."
        )
    return Groq(api_key=key)


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

            required_fields = ["sentiment", "confidence", "keywords", "summary"]
            missing = [f for f in required_fields if f not in result]
            if missing:
                raise ValueError(f"AI response missing fields: {missing}")

            return result

        except json.JSONDecodeError as e:
            last_error = f"Invalid JSON from API: {e}"
        except Exception as e:
            last_error = str(e)

            if "rate_limit" in str(e).lower() or "429" in str(e):
                time.sleep(2 * attempt)
                continue

        time.sleep(1)

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
        return "Medium"

    if sentiment == "negative" and confidence >= 0.7:
        return "High"
    if sentiment == "negative" and star_rating <= 2:
        return "High"
    if sentiment in ("negative", "neutral") and confidence < 0.7:
        return "Medium"
    if sentiment == "positive" and star_rating <= 2:
        return "Medium"
    return "Low"


def draft_reply(review_text: str, sentiment: str, max_retries: int = 3) -> str:
    """Generate a suggested seller reply to a customer review."""
    client = _get_client()

    system_prompt = (
        "You are a professional customer service assistant for an online seller. "
        "Given a customer review and its sentiment, write a short, warm, professional "
        "reply (2-4 sentences) the seller could send back to the customer. "
        "If the review is negative, acknowledge the issue and offer to make it right. "
        "If positive, thank them genuinely. Do not use markdown, just plain text."
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Sentiment: {sentiment}\\nReview: {review_text}"},
                ],
                temperature=0.4,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = str(e)
            time.sleep(1)

    return f"Could not generate reply: {last_error}"


def is_conflict(sentiment: str, star_rating) -> bool:
    """Flags cases where AI sentiment and star rating disagree strongly."""
    try:
        rating = float(star_rating)
    except (TypeError, ValueError):
        return False
    if sentiment == "negative" and rating >= 4:
        return True
    if sentiment == "positive" and rating <= 2:
        return True
    return False


def summarize_themes(review_summaries: list, max_retries: int = 3) -> dict:
    """Given a list of review summaries, extract top recurring themes."""
    client = _get_client()

    combined_text = chr(10).join(f"- {s}" for s in review_summaries)

    system_prompt = (
        "You are a customer feedback analyst. You will be given a list of review "
        "summaries. Respond with ONLY a JSON object (no markdown) with these fields: "
        "{\"top_complaints\": [list of up to 3 short strings], "
        "\"top_praises\": [list of up to 3 short strings], "
        "\"overall_takeaway\": one sentence string}"
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_text},
                ],
                temperature=0.3,
                max_tokens=400,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)
            return result
        except Exception as e:
            last_error = str(e)
            time.sleep(1)

    return {
        "top_complaints": [],
        "top_praises": [],
        "overall_takeaway": f"Could not generate summary: {last_error}",
    }


def aggregate_aspects(results: list) -> dict:
    """
    Combine per-review aspects into aspect-level counts and sentiment breakdown.
    results: list of analysis dicts (each may have an 'aspects' key).
    Returns: {aspect_name: {"positive": n, "neutral": n, "negative": n, "total": n}}
    """
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


def get_flag_reason(analysis: dict, star_rating, priority: str) -> dict:
    """
    Explain why a review was flagged and suggest a next action.
    Returns {"reason": str, "action": str}
    """
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
        reason = f"Negative review paired with a low {rating:.0f}⭐ rating."
        action = "Investigate the issue and reach out to the customer."
    elif rating is not None and sentiment == "positive" and rating <= 2:
        reason = f"AI reads positive tone but customer gave only {rating:.0f}⭐ - possible mismatch."
        action = "Review manually to confirm true sentiment."
    else:
        reason = "Flagged as high priority based on combined signals."
        action = "Review manually."

    return {"reason": reason, "action": action}
