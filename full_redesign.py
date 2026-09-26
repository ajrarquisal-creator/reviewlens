path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_import = "from src.genai_client import analyze_review, compute_priority, draft_reply"
new_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict"
content = content.replace(old_import, new_import)
print("import updated:", new_import in content)

old_success = """    progress_bar.empty()
    st.session_state["results_df"] = pd.DataFrame(results)
    st.success(f"\u2705 Analysis complete! Analyzed {len(results)} reviews.")"""

new_success = """    progress_bar.empty()
    results_df_temp = pd.DataFrame(results)
    st.session_state["results_df"] = results_df_temp

    with st.spinner("Summarizing overall themes..."):
        summaries_list = results_df_temp["Summary"].dropna().tolist()
        st.session_state["theme_summary"] = summarize_themes(summaries_list)

    st.success(f"\u2705 Analysis complete! Analyzed {len(results)} reviews.")"""

content = content.replace(old_success, new_success)
print("success block updated:", "theme_summary" in content)

old_overview = """    with tab_overview:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Analyzed", len(results_df))
        pct_negative = (results_df["AI Sentiment"] == "negative").mean() * 100
        m2.metric("% Negative", f"{pct_negative:.0f}%")
        m3.metric("Avg Confidence", f"{results_df[\x27Confidence\x27].mean():.2f}")
        flagged_count = (results_df["Priority"] == "High").sum()
        m4.metric("\U0001F6A9 High Priority", flagged_count)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(sentiment_distribution_chart(results_df), use_container_width=True)
        with chart_col2:
            st.plotly_chart(priority_distribution_chart(results_df), use_container_width=True)

        chart_col3, chart_col4 = st.columns(2)
        with chart_col3:
            st.plotly_chart(confidence_distribution_chart(results_df), use_container_width=True)
        with chart_col4:
            st.plotly_chart(rating_vs_sentiment_chart(results_df), use_container_width=True)"""

new_overview = """    with tab_overview:
        results_df["Conflict"] = results_df.apply(
            lambda r: is_conflict(r["AI Sentiment"], r["Star Rating"]), axis=1
        )

        st.markdown("### \U0001F4CA Key Performance Indicators")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Total Reviews", len(results_df))
        pct_positive = (results_df["AI Sentiment"] == "positive").mean() * 100
        k2.metric("Positive %", f"{pct_positive:.0f}%")
        pct_negative = (results_df["AI Sentiment"] == "negative").mean() * 100
        k3.metric("Negative %", f"{pct_negative:.0f}%")
        k4.metric("Avg Rating", f"{results_df[\x27Star Rating\x27].mean():.1f}\u2B50")
        flagged_count = (results_df["Priority"] == "High").sum()
        k5.metric("\U0001F6A9 High Priority", flagged_count)
        conflict_count = results_df["Conflict"].sum()
        k6.metric("\u26A1 Conflicts", conflict_count)

        st.divider()
        st.markdown("### \U0001F4C8 Main Overview")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(sentiment_distribution_chart(results_df), use_container_width=True)
        with chart_col2:
            st.plotly_chart(rating_vs_sentiment_chart(results_df), use_container_width=True)

        if "theme_summary" in st.session_state:
            theme = st.session_state["theme_summary"]
            with st.container(border=True):
                st.markdown("**\U0001F4A1 Overall AI Summary**")
                st.write(theme.get("overall_takeaway", "N/A"))

        st.divider()
        st.markdown("### \U0001F50D Customer Insights")

        insight_col1, insight_col2 = st.columns(2)
        if "theme_summary" in st.session_state:
            theme = st.session_state["theme_summary"]
            with insight_col1:
                st.markdown("**\u2705 Top Positive Themes**")
                for p in theme.get("top_praises", []):
                    st.markdown(f"- {p}")
            with insight_col2:
                st.markdown("**\u26A0\uFE0F Top Pain Points**")
                for c in theme.get("top_complaints", []):
                    st.markdown(f"- {c}")
        else:
            st.info("Run analysis to see AI-generated insights here.")

        with st.expander("More charts: Priority & Confidence distribution"):
            chart_col3, chart_col4 = st.columns(2)
            with chart_col3:
                st.plotly_chart(priority_distribution_chart(results_df), use_container_width=True)
            with chart_col4:
                st.plotly_chart(confidence_distribution_chart(results_df), use_container_width=True)"""

content = content.replace(old_overview, new_overview)
print("overview block updated:", "Key Performance Indicators" in content)

open(path, "w", encoding="utf-8").write(content)
print("File saved.")
