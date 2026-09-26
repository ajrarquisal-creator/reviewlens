# ReviewLens 🔍

A Generative AI web application that analyzes real Amazon product reviews using an LLM (via Groq) — extracting sentiment, aspects, keywords, and summaries, detecting priority and sentiment/rating conflicts, and generating actionable business recommendations.

## Project Pitch

ReviewLens is a seller review triage and intelligence tool. It takes a cleaned sample of Amazon product reviews, sends each one to a GenAI model (via the Groq API) for structured analysis, and computes an action-priority flag (High/Medium/Low) from the sentiment, confidence, and star rating. It also detects cases where the AI-read sentiment conflicts with the star rating, extracts specific product aspects (e.g. taste, shipping, packaging) with their own sentiment, and generates an AI-written executive summary and a set of concrete recommendations. Instead of reading hundreds of reviews by hand, a seller can open the dashboard and immediately see what customers think, what needs attention, and what to do next.

## Dataset

- **File:** `data/reviews_small.csv`
- **Source:** Amazon Fine Food Reviews dataset (Kaggle / Stanford SNAP)
- **Columns used:** `Id`, `Text`, `Summary`, `Score`
- **Size after cleaning:** 499 reviews

## Intended Users

Students, instructors, and small business owners who want a fast, GenAI-powered overview of customer sentiment and actionable insight from product reviews.

## Features

- Loads and cleans a CSV dataset of Amazon reviews
- Randomly samples a configurable number of reviews to control API cost
- Sends each sampled review to Groq's `openai/gpt-oss-20b` model with a structured prompt
- Returns consistent JSON: sentiment, confidence, keywords, summary, and per-aspect sentiment
- **KPI dashboard**: total reviews, positive/negative %, average rating, high-priority count, AI/rating conflict count
- **AI-generated overall summary** and **actionable recommendations** based on the full analyzed batch
- **Aspect/topic analysis**: extracts specific product aspects (taste, shipping, packaging, etc.) with per-aspect sentiment breakdown
- **Action Center**: each flagged review shows *why* it was flagged and a suggested next action
- **Conflicts tab**: surfaces reviews where AI sentiment disagrees with the star rating, with a plain-language explanation
- **Review Detail View**: inspect any single analyzed review in full, including all extracted aspects
- **AI-drafted reply suggestions** for high-priority reviews, generated on demand
- Interactive, filterable, searchable results table with CSV export
- Live progress feedback during analysis (running sentiment tally as it processes)
- In-session caching — re-running analysis on an already-seen review reuses the cached result instead of re-calling the API
- Analysis only runs on explicit user action (Run Analysis button) — no automatic API calls
- Handles missing API key, missing dataset, validation errors, rate limits, and malformed AI responses

## Data Cleaning

- Kept only relevant columns: `Id`, `Text`, `Summary`, `Score`
- Dropped rows with missing `Text` or `Score`
- Dropped duplicate reviews (by text)
- Stripped URLs and HTML tags from review text
- Normalized whitespace
- Removed empty or very short (<10 character) reviews

## GenAI Integration

- **Provider:** Groq API
- **Model:** `openai/gpt-oss-20b`
- **Prompt design:** Structured system prompts instruct the model to return only a JSON object with defined fields (sentiment, confidence, keywords, summary, aspects for per-review analysis; complaints/praises/takeaway for theme summarization; a recommendation list for business advice) — no markdown or extra text — using the API's `response_format: json_object` mode for reliability.
- **Reliability:** Includes retry logic (up to 3 attempts), rate-limit backoff, JSON validation, and safe fallback results (e.g. `sentiment: "unknown"`) if all retries fail, so the app never crashes on a bad API response.

## Cost-Control Strategy

- Dataset is randomly sampled down to a user-selected number of records (5–100) before any API calls are made
- Analysis is triggered only by an explicit "Run Analysis" button click — never on page load or refresh
- In-session caching avoids re-calling the API for reviews already analyzed in the current session
- Per-review analysis calls are capped at `max_tokens=600`; aggregate summary/recommendation calls are capped at `max_tokens=700`

## Visualizations

1. **Sentiment Distribution** — bar chart of positive/neutral/negative/unknown counts
2. **Star Rating vs AI Sentiment** — stacked bar chart comparing the review's original star rating to the AI's sentiment call
3. **Aspect Breakdown** — stacked bar chart of the most-mentioned product aspects, colored by sentiment
4. **Priority Distribution** and **Confidence Distribution** — available in an expandable "more charts" section

## Action Priority Logic

Each analyzed review is assigned a priority tier to help a seller triage quickly:

- **High** — negative sentiment with confidence ≥ 0.7, OR negative sentiment paired with a 1–2 star rating (a confirmed real complaint)
- **Medium** — negative/neutral sentiment with lower confidence, a failed analysis, or a positive/low-star mismatch worth a glance
- **Low** — everything else (confirmed positive reviews, or low-confidence noise)

The Action Center in the "Flagged for Action" tab explains *why* each high-priority review was flagged and suggests a concrete next step, alongside an AI-drafted reply and a one-click CSV export.

## Conflict Detection

A review is flagged as a conflict when the AI-read sentiment strongly disagrees with the star rating (e.g. a 4-5 star review read as negative, or a 1-2 star review read as positive). The dedicated Conflicts tab lists each case with a plain-language explanation.

## Installation

```powershell
git clone https://github.com/ajrarquisal-creator/reviewlens.git
cd reviewlens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the project root with:

```text
GROQ_API_KEY=your_api_key_here
```

Get a free key at https://console.groq.com/keys. Never commit this file — it is already listed in `.gitignore`.

## Running the App

```powershell
streamlit run app.py
```

## Project Structure

```text
reviewlens/
├── app.py
├── requirements.txt
├── README.md
├── .env                  (not committed)
├── .gitignore
├── data/
│   └── reviews_small.csv
├── src/
│   ├── load_data.py
│   ├── genai_client.py
│   └── visualize.py
└── .streamlit/
    └── config.toml
```

## Findings

Across sampled batches of the Amazon Fine Food Reviews dataset, the majority of reviews skew positive, with recurring positive themes around taste and value, and recurring complaints concentrated in a small number of aspects such as packaging and shipping. AI-detected sentiment/rating conflicts are relatively rare but genuinely useful to surface, since they highlight reviews where the written sentiment doesn't match the star rating a customer left.

## Limitations

- Sentiment/aspect extraction quality depends on the underlying Groq-hosted model and can occasionally fail to return valid JSON on longer or more rambling reviews (handled gracefully with a fallback "unknown" result)
- The dataset is a static, pre-sampled CSV rather than live review data
- Caching is in-memory per session only and does not persist across app restarts

## Future Improvements

- Persistent caching (e.g. to disk or a database) across sessions
- PDF/exportable report generation
- Time-based trend analysis using review timestamps
- Support for live review data via an API connector

## Author

Apple Clariss Montero — BSIT student, North Eastern Mindanao State University (NEMSU)
