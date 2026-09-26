path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict, aggregate_aspects, get_flag_reason"
new_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict, aggregate_aspects, get_flag_reason, explain_conflict"
content = content.replace(old_import, new_import)
print("import updated:", new_import in content)

old_tabs = """    tab_overview, tab_queue, tab_flagged = st.tabs(
        ["\U0001F4CA Overview", "\U0001F4CB Review Queue", "\U0001F6A9 Flagged for Action"]
    )"""

new_tabs = """    tab_overview, tab_queue, tab_flagged, tab_conflicts = st.tabs(
        ["\U0001F4CA Overview", "\U0001F4CB Review Queue", "\U0001F6A9 Flagged for Action", "\u26A1 Conflicts"]
    )"""

content = content.replace(old_tabs, new_tabs)
print("tabs updated:", "tab_conflicts" in content)

marker = "else:\n    st.info(\"\U0001F446 Configure settings above and click **Run Analysis** to begin.\")"

conflicts_tab_code = """
    # ----- Conflicts tab -----
    with tab_conflicts:
        results_df["Conflict"] = results_df.apply(
            lambda r: is_conflict(r["AI Sentiment"], r["Star Rating"]), axis=1
        )
        conflict_df = results_df[results_df["Conflict"]].drop(columns=["Error", "Conflict"])

        if conflict_df.empty:
            st.info("No sentiment/rating conflicts detected in this batch. \U0001F44D")
        else:
            st.warning(f"{len(conflict_df)} review(s) show a mismatch between AI sentiment and star rating.")
            for idx, row in conflict_df.reset_index(drop=True).iterrows():
                with st.expander(f"Review: {row['Review'][:80]}..."):
                    explanation = explain_conflict(row["AI Sentiment"], row["Star Rating"])
                    st.write(f"**Star Rating:** {row['Star Rating']}\u2B50 | **AI Sentiment:** {row['AI Sentiment']} | **Confidence:** {row['Confidence']:.0%}")
                    st.error(f"**Conflict:** {explanation}")
                    st.write(f"**Summary:** {row['Summary']}")

            conflict_csv = conflict_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "\u2B07\uFE0F Export conflicts to CSV",
                data=conflict_csv,
                file_name="reviewlens_conflicts.csv",
                mime="text/csv",
            )

"""

if marker in content:
    content = content.replace(marker, conflicts_tab_code + marker)
    print("Conflicts tab code inserted: True")
else:
    print("Conflicts tab code inserted: False - marker not found")

open(path, "w", encoding="utf-8").write(content)
