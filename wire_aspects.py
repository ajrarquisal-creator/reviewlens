path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_import1 = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict"
new_import1 = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict, aggregate_aspects"
content = content.replace(old_import1, new_import1)
print("import 1 updated:", new_import1 in content)

old_import2 = """from src.visualize import (
    sentiment_distribution_chart,
    confidence_distribution_chart,
    rating_vs_sentiment_chart,
    priority_distribution_chart,
)"""
new_import2 = """from src.visualize import (
    sentiment_distribution_chart,
    confidence_distribution_chart,
    rating_vs_sentiment_chart,
    priority_distribution_chart,
    aspect_breakdown_chart,
)"""
content = content.replace(old_import2, new_import2)
print("import 2 updated:", "aspect_breakdown_chart," in content)

old_loop = """        analysis = analyze_review(row.Text)
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
        })"""

new_loop = """        analysis = analyze_review(row.Text)
        priority = compute_priority(analysis, row.Score)
        raw_analyses.append(analysis)
        results.append({
            "Review": row.Text[:150] + ("..." if len(row.Text) > 150 else ""),
            "Star Rating": row.Score,
            "AI Sentiment": analysis.get("sentiment", "unknown"),
            "Confidence": analysis.get("confidence", 0.0),
            "Priority": priority,
            "Keywords": ", ".join(analysis.get("keywords", [])),
            "Summary": analysis.get("summary", ""),
            "Error": analysis.get("error", False),
        })"""

content = content.replace(old_loop, new_loop)
print("loop updated:", "raw_analyses.append" in content)

old_results_init = """    results = []
    progress_bar = st.progress(0, text="Starting analysis...")"""
new_results_init = """    results = []
    raw_analyses = []
    progress_bar = st.progress(0, text="Starting analysis...")"""
content = content.replace(old_results_init, new_results_init)
print("results init updated:", "raw_analyses = []" in content)

old_success = """    with st.spinner("Summarizing overall themes..."):
        summaries_list = results_df_temp["Summary"].dropna().tolist()
        st.session_state["theme_summary"] = summarize_themes(summaries_list)"""
new_success = """    with st.spinner("Summarizing overall themes..."):
        summaries_list = results_df_temp["Summary"].dropna().tolist()
        st.session_state["theme_summary"] = summarize_themes(summaries_list)
        st.session_state["aspect_summary"] = aggregate_aspects(raw_analyses)"""
content = content.replace(old_success, new_success)
print("aspect aggregation call added:", "aspect_summary" in content)

old_insights_end = """        with st.expander("More charts: Priority & Confidence distribution"):"""
new_insights_end = """        if "aspect_summary" in st.session_state and st.session_state["aspect_summary"]:
            aspect_fig = aspect_breakdown_chart(st.session_state["aspect_summary"])
            if aspect_fig:
                st.plotly_chart(aspect_fig, use_container_width=True)

        with st.expander("More charts: Priority & Confidence distribution"):"""
content = content.replace(old_insights_end, new_insights_end)
print("aspect chart display added:", "aspect_breakdown_chart(st.session_state" in content)

open(path, "w", encoding="utf-8").write(content)
print("Saved.")
