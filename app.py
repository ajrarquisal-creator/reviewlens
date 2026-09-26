import streamlit as st
import pandas as pd
import os

from src.load_data import load_dataset, clean_dataset, sample_dataset, validate_dataset
from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict
from src.visualize import (
    sentiment_distribution_chart,
    confidence_distribution_chart,
    rating_vs_sentiment_chart,
    priority_distribution_chart,
)


def style_results(df):
    def color_sentiment(val):
        colors = {"positive": "#D1FADF", "negative": "#FEE4E2", "neutral": "#F2F4F7", "unknown": "#FEF0C7"}
        return f"background-color: {colors.get(val, '')}"

    def color_priority(val):
        colors = {"High": "#FEE4E2", "Medium": "#FEF0C7", "Low": "#D1FADF"}
        return f"background-color: {colors.get(val, '')}"

    styler = df.style
    if "AI Sentiment" in df.columns:
        styler = styler.map(color_sentiment, subset=["AI Sentiment"])
    if "Priority" in df.columns:
        styler = styler.map(color_priority, subset=["Priority"])
    return styler

st.set_page_config(page_title="ReviewLens", page_icon="🔍", layout="wide")

st.title("ReviewLens 🔍")
st.write(
    "A seller review triage tool — uses GenAI to read customer reviews and flag "
    "which ones need action first, so you are not reading hundreds of reviews by hand."
)

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

with st.container(border=True):
    st.subheader("Dataset Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total cleaned reviews available", len(clean_df))
    col2.metric("Columns", ", ".join(clean_df.columns))
    with st.expander("Preview raw cleaned data"):
        st.dataframe(clean_df.head(10))

# ----- Controls -----
with st.container(border=True):
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
        priority = compute_priority(analysis, row.Score)
        results.append({
            "Review": row.Text[:150] + ("..." if len(row.Text) > 150 else ""),
            "Star Rating": row.Score,
            "AI Sentiment": analysis.get("sentiment", "unknown"),
            "Confidence": analysis.get("confidence", 0.0),
            "Priority": priority,
            "Keywords": ", ".join(analysis.get("keywords", [])),
            "Summary": analysis.get("summary", ""),
            "Error": analysis.get("error", False),
        })

    progress_bar.empty()
    results_df_temp = pd.DataFrame(results)
    st.session_state["results_df"] = results_df_temp

    with st.spinner("Summarizing overall themes..."):
        summaries_list = results_df_temp["Summary"].dropna().tolist()
        st.session_state["theme_summary"] = summarize_themes(summaries_list)

    st.success(f"✅ Analysis complete! Analyzed {len(results)} reviews.")

# ----- Display results -----
if "results_df" in st.session_state:
    results_df = st.session_state["results_df"]

    error_count = results_df["Error"].sum()
    if error_count > 0:
        st.warning(f"⚠️ {error_count} review(s) failed to analyze and show as 'unknown'.")

    tab_overview, tab_queue, tab_flagged = st.tabs(
        ["📊 Overview", "📋 Review Queue", "🚩 Flagged for Action"]
    )

    # ----- Overview tab -----
    with tab_overview:
        results_df["Conflict"] = results_df.apply(
            lambda r: is_conflict(r["AI Sentiment"], r["Star Rating"]), axis=1
        )

        st.markdown("### 📊 Key Performance Indicators")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Total Reviews", len(results_df))
        pct_positive = (results_df["AI Sentiment"] == "positive").mean() * 100
        k2.metric("Positive %", f"{pct_positive:.0f}%")
        pct_negative = (results_df["AI Sentiment"] == "negative").mean() * 100
        k3.metric("Negative %", f"{pct_negative:.0f}%")
        k4.metric("Avg Rating", f"{results_df['Star Rating'].mean():.1f}⭐")
        flagged_count = (results_df["Priority"] == "High").sum()
        k5.metric("🚩 High Priority", flagged_count)
        conflict_count = results_df["Conflict"].sum()
        k6.metric("⚡ Conflicts", conflict_count)

        st.divider()
        st.markdown("### 📈 Main Overview")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(sentiment_distribution_chart(results_df), use_container_width=True)
        with chart_col2:
            st.plotly_chart(rating_vs_sentiment_chart(results_df), use_container_width=True)

        if "theme_summary" in st.session_state:
            theme = st.session_state["theme_summary"]
            with st.container(border=True):
                st.markdown("**💡 Overall AI Summary**")
                st.write(theme.get("overall_takeaway", "N/A"))

        st.divider()
        st.markdown("### 🔍 Customer Insights")

        insight_col1, insight_col2 = st.columns(2)
        if "theme_summary" in st.session_state:
            theme = st.session_state["theme_summary"]
            with insight_col1:
                st.markdown("**✅ Top Positive Themes**")
                for p in theme.get("top_praises", []):
                    st.markdown(f"- {p}")
            with insight_col2:
                st.markdown("**⚠️ Top Pain Points**")
                for c in theme.get("top_complaints", []):
                    st.markdown(f"- {c}")
        else:
            st.info("Run analysis to see AI-generated insights here.")

        with st.expander("More charts: Priority & Confidence distribution"):
            chart_col3, chart_col4 = st.columns(2)
            with chart_col3:
                st.plotly_chart(priority_distribution_chart(results_df), use_container_width=True)
            with chart_col4:
                st.plotly_chart(confidence_distribution_chart(results_df), use_container_width=True)

    # ----- Review Queue tab -----
    with tab_queue:
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

        st.dataframe(style_results(filtered.drop(columns=["Error"])), use_container_width=True)
        st.caption(f"Showing {len(filtered)} of {len(results_df)} analyzed reviews.")

        csv_data = filtered.drop(columns=["Error"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export queue to CSV",
            data=csv_data,
            file_name="reviewlens_results.csv",
            mime="text/csv",
        )

    # ----- Flagged for Action tab -----
    with tab_flagged:
        flagged_df = results_df[results_df["Priority"] == "High"].drop(columns=["Error"])
        if flagged_df.empty:
            st.info("No high-priority reviews in this batch. 🎉")
        else:
            st.warning(f"{len(flagged_df)} review(s) need attention first.")
            st.dataframe(style_results(flagged_df), use_container_width=True)

            flagged_csv = flagged_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export flagged reviews to CSV",
                data=flagged_csv,
                file_name="reviewlens_flagged.csv",
                mime="text/csv",
            )

            st.subheader("✍️ Draft Replies")
            for idx, row in flagged_df.reset_index(drop=True).iterrows():
                with st.expander(f"Review: {row['Review'][:80]}..."):
                    st.write(f"**Sentiment:** {row['AI Sentiment']} | **Star Rating:** {row['Star Rating']}")
                    st.write(f"**Summary:** {row['Summary']}")
                    reply_key = f"reply_{idx}"
                    if st.button(f"✍️ Draft Reply", key=f"draft_btn_{idx}"):
                        with st.spinner("Drafting reply..."):
                            reply = draft_reply(row["Review"], row["AI Sentiment"])
                            st.session_state[reply_key] = reply
                    if reply_key in st.session_state:
                        st.text_area("Suggested reply", st.session_state[reply_key], key=f"reply_area_{idx}")
else:
    st.info("👆 Configure settings above and click **Run Analysis** to begin.")
