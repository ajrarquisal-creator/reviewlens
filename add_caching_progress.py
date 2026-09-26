path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_loop_full = """    sample_df = sample_dataset(clean_df, n=num_records)

    results = []
    raw_analyses = []
    progress_bar = st.progress(0, text="Starting analysis...")

    for i, row in enumerate(sample_df.itertuples(), start=1):
        progress_bar.progress(
            i / len(sample_df),
            text=f"Analyzing {i} of {len(sample_df)} records...",
        )
        analysis = analyze_review(row.Text)
        priority = compute_priority(analysis, row.Score)
        raw_analyses.append(analysis)
        results.append({
            "Review": row.Text[:150] + ("..." if len(row.Text) > 150 else ""),
            "Full Review": row.Text,
            "Star Rating": row.Score,
            "AI Sentiment": analysis.get("sentiment", "unknown"),
            "Confidence": analysis.get("confidence", 0.0),
            "Priority": priority,
            "Keywords": ", ".join(analysis.get("keywords", [])),
            "Summary": analysis.get("summary", ""),
            "Aspects": analysis.get("aspects", []),
            "Error": analysis.get("error", False),
        })"""

new_loop_full = """    sample_df = sample_dataset(clean_df, n=num_records)

    if "analysis_cache" not in st.session_state:
        st.session_state["analysis_cache"] = {}
    cache = st.session_state["analysis_cache"]

    results = []
    raw_analyses = []
    tally = {"positive": 0, "neutral": 0, "negative": 0, "unknown": 0}
    cache_hits = 0
    progress_bar = st.progress(0, text="Starting analysis...")

    for i, row in enumerate(sample_df.itertuples(), start=1):
        if row.Text in cache:
            analysis = cache[row.Text]
            cache_hits += 1
        else:
            analysis = analyze_review(row.Text)
            cache[row.Text] = analysis

        sentiment_key = analysis.get("sentiment", "unknown")
        tally[sentiment_key] = tally.get(sentiment_key, 0) + 1

        progress_bar.progress(
            i / len(sample_df),
            text=(
                f"Analyzing {i} of {len(sample_df)} \u2014 "
                f"\u2705 {tally[\x27positive\x27]} positive, "
                f"\u26AA {tally[\x27neutral\x27]} neutral, "
                f"\u274C {tally[\x27negative\x27]} negative"
                + (f" ({cache_hits} cached)" if cache_hits else "")
            ),
        )

        priority = compute_priority(analysis, row.Score)
        raw_analyses.append(analysis)
        results.append({
            "Review": row.Text[:150] + ("..." if len(row.Text) > 150 else ""),
            "Full Review": row.Text,
            "Star Rating": row.Score,
            "AI Sentiment": analysis.get("sentiment", "unknown"),
            "Confidence": analysis.get("confidence", 0.0),
            "Priority": priority,
            "Keywords": ", ".join(analysis.get("keywords", [])),
            "Summary": analysis.get("summary", ""),
            "Aspects": analysis.get("aspects", []),
            "Error": analysis.get("error", False),
        })"""

if old_loop_full in content:
    content = content.replace(old_loop_full, new_loop_full)
    print("Loop updated with caching and live tally: True")
else:
    print("Loop updated with caching and live tally: False - not found")

open(path, "w", encoding="utf-8").write(content)
