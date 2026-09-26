path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_import = "from src.genai_client import analyze_review, compute_priority, draft_reply"
new_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes"
if old_import in content:
    content = content.replace(old_import, new_import)
    print("Updated import.")
else:
    print("Import line not found.")

old_success_line = """    progress_bar.empty()
    st.session_state["results_df"] = pd.DataFrame(results)
    st.success(f"\u2705 Analysis complete! Analyzed {len(results)} reviews.")"""

new_success_line = """    progress_bar.empty()
    results_df_temp = pd.DataFrame(results)
    st.session_state["results_df"] = results_df_temp

    with st.spinner("Summarizing overall themes..."):
        summaries_list = results_df_temp["Summary"].dropna().tolist()
        theme_result = summarize_themes(summaries_list)
        st.session_state["theme_summary"] = theme_result

    st.success(f"\u2705 Analysis complete! Analyzed {len(results)} reviews.")"""

if old_success_line in content:
    content = content.replace(old_success_line, new_success_line)
    print("Added theme summary call after analysis.")
else:
    print("Success line not found - manual check needed.")

open(path, "w", encoding="utf-8").write(content)
