import streamlit as st
import pandas as pd
import os

from src.load_data import load_dataset, clean_dataset, sample_dataset, validate_dataset
from src.genai_client import analyze_review
from src.visualize import (
    sentiment_distribution_chart,
    confidence_distribution_chart,
    rating_vs_sentiment_chart,
)

st.set_page_config(page_title="ReviewLens", page_icon="🔍", layout="wide")

st.title("ReviewLens 🔍")
st.write("Analyze real Amazon product reviews using GenAI — sentiment, keywords, and summaries.")

# ----- Load & prepare dataset -----
try:
    raw_df = load_dataset()
    validate_dataset(raw_df)
    clean_df = clean_dataset(raw_df)
except FileNotFoundError:
    st.error("❌ Dataset not found. Make sure `data/reviews_small.csv` exists.")
    st.stop()
except ValueError as e:
    st.error(f"❌ Dataset validation failed: {e}")
    st.stop()

if clean_df.empty:
    st.error("❌ Dataset is empty after cleaning. Nothing to analyze.")
    st.stop()

st.subheader("Dataset Overview")
col1, col2 = st.columns(2)
col1.metric("Total cleaned reviews available", len(clean_df))
col2.metric("Columns", ", ".join(clean_df.columns))

with st.expander("Preview raw cleaned data"):
    st.dataframe(clean_df.head(10))

# ----- Controls -----
st.subheader("Analysis Settings")

max_available = min(len(clean_df), 100)
num_records = st.slider(
    "Number of records to analyze",
    min_value=5,
    max_value=max_available,
    value=min(20, max_available),
    help="Fewer records = faster and cheaper. Analysis calls the Groq API once per record.",
)

confidence_threshold = st.slider(
    "Minimum confidence to display",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.05,
)

run_clicked = st.button("🚀 Run Analysis", type="primary")

# ----- Run analysis (only on button click) -----
if run_clicked:
    if not os.getenv("GROQ_API_KEY"):
        st.error("❌ GROQ_API_KEY not found. Please set it in your `.env` file.")
        st.stop()

    sample_df = sample_dataset(clean_df, n=num_records)

    results = []
    progress_bar = st.progress(0, text="Starting analysis...")

    for i, row in enumerate(sample_df.itertuples(), start=1):
        progress_bar.progress(
            i / len(sample_df),
            text=f"Analyzing {i} of {len(sample_df)} records...",
        )
        analysis = analyze_review(row.Text)
        results.append({
            "Review": row.Text[:150] + ("..." if len(row.Text) > 150 else ""),
            "Star Rating": row.Score,
            "AI Sentiment": analysis.get("sentiment", "unknown"),
            "Confidence": analysis.get("confidence", 0.0),
            "Keywords": ", ".join(analysis.get("keywords", [])),
            "Summary": analysis.get("summary", ""),
            "Error": analysis.get("error", False),
        })

    progress_bar.empty()
    st.session_state["results_df"] = pd.DataFrame(results)
    st.success(f"✅ Analysis complete! Analyzed {len(results)} reviews.")

# ----- Display results -----
if "results_df" in st.session_state:
    results_df = st.session_state["results_df"]

    error_count = results_df["Error"].sum()
    if error_count > 0:
        st.warning(f"⚠️ {error_count} review(s) failed to analyze and show as 'unknown'.")

    st.subheader("Results")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        sentiment_filter = st.multiselect(
            "Filter by sentiment",
            options=sorted(results_df["AI Sentiment"].unique()),
            default=sorted(results_df["AI Sentiment"].unique()),
        )
    with filter_col2:
        search_term = st.text_input("Search in review text")

    filtered = results_df[
        (results_df["AI Sentiment"].isin(sentiment_filter))
        & (results_df["Confidence"] >= confidence_threshold)
    ]
    if search_term:
        filtered = filtered[filtered["Review"].str.contains(search_term, case=False, na=False)]

    st.dataframe(filtered.drop(columns=["Error"]), use_container_width=True)
    st.caption(f"Showing {len(filtered)} of {len(results_df)} analyzed reviews.")

    st.subheader("Visual Insights")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(sentiment_distribution_chart(results_df), use_container_width=True)
    with chart_col2:
        st.plotly_chart(confidence_distribution_chart(results_df), use_container_width=True)

    st.plotly_chart(rating_vs_sentiment_chart(results_df), use_container_width=True)
else:
    st.info("👆 Configure settings above and click **Run Analysis** to begin.")