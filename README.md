\# ReviewLens 🔍



A Generative AI web application that analyzes real Amazon product reviews using an LLM — extracting sentiment, keywords, and summaries, then visualizing the results interactively.



\## Project Pitch



ReviewLens is a seller review triage tool. It takes a cleaned sample of Amazon product reviews, sends each one to a GenAI model (via the Groq API) for structured analysis, and computes an action-priority flag (High/Medium/Low) from the sentiment, confidence, and star rating. Instead of reading hundreds of reviews by hand, a seller can jump straight to the 'Flagged for Action' tab and see which reviews need a response first.



\## Dataset



\- \*\*File:\*\* `data/reviews\_small.csv`

\- \*\*Source:\*\* Amazon Fine Food Reviews dataset (Kaggle / Stanford SNAP)

\- \*\*Columns used:\*\* `Id`, `Text`, `Summary`, `Score`

\- \*\*Size after cleaning:\*\* 499 reviews



\## Intended Users



Students, instructors, and small business owners who want a fast, GenAI-powered overview of customer sentiment in product reviews.



\## Features



\- Loads and cleans a CSV dataset of Amazon reviews

\- Randomly samples a configurable number of reviews to control API cost

\- Sends each sampled review to Groq's `openai/gpt-oss-20b` model with a structured prompt

\- Returns consistent JSON: sentiment, confidence, keywords, summary

\- Displays results in an interactive, filterable, searchable table

\- Visualizes sentiment distribution, confidence distribution, and star rating vs. AI sentiment

\- Analysis only runs on explicit user action (Run Analysis button) — no automatic API calls

\- Handles missing API key, missing dataset, validation errors, rate limits, and malformed AI responses



\## Data Cleaning



\- Kept only relevant columns: `Id`, `Text`, `Summary`, `Score`

\- Dropped rows with missing `Text` or `Score`

\- Dropped duplicate reviews (by text)

\- Stripped URLs and HTML tags from review text

\- Normalized whitespace

\- Removed empty or very short (<10 character) reviews



\## GenAI Integration



\- \*\*Provider:\*\* Groq API

\- \*\*Model:\*\* `openai/gpt-oss-20b`

\- \*\*Prompt design:\*\* A system prompt instructs the model to return only a JSON object with `sentiment`, `confidence`, `keywords`, and `summary` fields — no markdown or extra text — using the API's `response\_format: json\_object` mode for reliability.

\- \*\*Reliability:\*\* Includes retry logic (up to 3 attempts), rate-limit backoff, JSON validation, and a safe fallback result (`sentiment: "unknown"`) if all retries fail, so the app never crashes on a bad API response.



\## Cost-Control Strategy



\- Dataset is randomly sampled down to a user-selected number of records (5–100) before any API calls are made

\- Analysis is triggered only by an explicit "Run Analysis" button click — never on page load or refresh

\- Each review is sent as a single, small API call with a capped `max\_tokens` of 300



\## Visualizations



1\. \*\*Sentiment Distribution\*\* — bar chart of positive/neutral/negative/unknown counts

2\. \*\*Confidence Score Distribution\*\* — histogram of the model's confidence scores

3\. \*\*Star Rating vs AI Sentiment\*\* — stacked bar chart comparing the review's original star rating to the AI's sentiment call, useful for spotting disagreements (e.g. a 5-star review flagged negative)



\## Installation



```powershell

git clone YOUR\_REPOSITORY\_URL

cd genai\_app

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

```



\## Environment Setup



Create a `.env` file in the project root with:



## Action Priority Logic

Each analyzed review is assigned a priority tier to help a seller triage quickly:

- **High** — negative sentiment with confidence ≥ 0.7, OR negative sentiment paired with a 1–2 star rating (a confirmed real complaint)
- **Medium** — negative/neutral sentiment with lower confidence, a failed analysis, or a positive/low-star mismatch worth a glance
- **Low** — everything else (confirmed positive reviews, or low-confidence noise)

The Overview tab shows a priority breakdown chart, and the "Flagged for Action" tab filters straight to High-priority reviews with a one-click CSV export.
