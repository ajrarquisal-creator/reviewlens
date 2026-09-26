path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict, aggregate_aspects, get_flag_reason, explain_conflict"
new_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict, aggregate_aspects, get_flag_reason, explain_conflict, generate_recommendations"
content = content.replace(old_import, new_import)
print("import updated:", new_import in content)

old_call = """    with st.spinner("Summarizing overall themes..."):
        summaries_list = results_df_temp["Summary"].dropna().tolist()
        st.session_state["theme_summary"] = summarize_themes(summaries_list)
        st.session_state["aspect_summary"] = aggregate_aspects(raw_analyses)"""

new_call = """    with st.spinner("Summarizing overall themes..."):
        summaries_list = results_df_temp["Summary"].dropna().tolist()
        theme_summary = summarize_themes(summaries_list)
        aspect_summary = aggregate_aspects(raw_analyses)
        st.session_state["theme_summary"] = theme_summary
        st.session_state["aspect_summary"] = aspect_summary

        conflict_count_temp = results_df_temp.apply(
            lambda r: is_conflict(r["AI Sentiment"], r["Star Rating"]), axis=1
        ).sum()
        high_priority_count_temp = (results_df_temp["Priority"] == "High").sum()
        st.session_state["recommendations"] = generate_recommendations(
            theme_summary, aspect_summary, conflict_count_temp, high_priority_count_temp
        )"""

content = content.replace(old_call, new_call)
print("recommendations call added:", "st.session_state[\"recommendations\"]" in content)

old_summary_box = """        if "theme_summary" in st.session_state:
            theme = st.session_state["theme_summary"]
            with st.container(border=True):
                st.markdown("**\U0001F4A1 Overall AI Summary**")
                st.write(theme.get("overall_takeaway", "N/A"))"""

new_summary_box = """        if "theme_summary" in st.session_state:
            theme = st.session_state["theme_summary"]
            with st.container(border=True):
                st.markdown("**\U0001F4A1 Overall AI Summary**")
                st.write(theme.get("overall_takeaway", "N/A"))

        if "recommendations" in st.session_state:
            with st.container(border=True):
                st.markdown("**\U0001F3AF Recommendations**")
                for rec in st.session_state["recommendations"]:
                    st.markdown(f"- {rec}")"""

content = content.replace(old_summary_box, new_summary_box)
print("recommendations display added:", "\U0001F3AF Recommendations" in content)

open(path, "w", encoding="utf-8").write(content)
