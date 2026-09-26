path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_import = "from src.genai_client import analyze_review, compute_priority"
new_import = "from src.genai_client import analyze_review, compute_priority, draft_reply"
if old_import in content:
    content = content.replace(old_import, new_import)
    print("Updated import.")
else:
    print("Import line not found - may already be updated.")

old_flagged_block = """    with tab_flagged:
        flagged_df = results_df[results_df["Priority"] == "High"].drop(columns=["Error"])
        if flagged_df.empty:
            st.info("No high-priority reviews in this batch. \U0001F389")
        else:
            st.warning(f"{len(flagged_df)} review(s) need attention first.")
            st.dataframe(style_results(flagged_df), use_container_width=True)

            flagged_csv = flagged_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "\u2B07\uFE0F Export flagged reviews to CSV",
                data=flagged_csv,
                file_name="reviewlens_flagged.csv",
                mime="text/csv",
            )"""

new_flagged_block = """    with tab_flagged:
        flagged_df = results_df[results_df["Priority"] == "High"].drop(columns=["Error"])
        if flagged_df.empty:
            st.info("No high-priority reviews in this batch. \U0001F389")
        else:
            st.warning(f"{len(flagged_df)} review(s) need attention first.")
            st.dataframe(style_results(flagged_df), use_container_width=True)

            flagged_csv = flagged_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "\u2B07\uFE0F Export flagged reviews to CSV",
                data=flagged_csv,
                file_name="reviewlens_flagged.csv",
                mime="text/csv",
            )

            st.subheader("\u270D\uFE0F Draft Replies")
            for idx, row in flagged_df.reset_index(drop=True).iterrows():
                with st.expander(f"Review: {row['Review'][:80]}..."):
                    st.write(f"**Sentiment:** {row['AI Sentiment']} | **Star Rating:** {row['Star Rating']}")
                    st.write(f"**Summary:** {row['Summary']}")
                    reply_key = f"reply_{idx}"
                    if st.button(f"\u270D\uFE0F Draft Reply", key=f"draft_btn_{idx}"):
                        with st.spinner("Drafting reply..."):
                            reply = draft_reply(row["Review"], row["AI Sentiment"])
                            st.session_state[reply_key] = reply
                    if reply_key in st.session_state:
                        st.text_area("Suggested reply", st.session_state[reply_key], key=f"reply_area_{idx}")"""

if old_flagged_block in content:
    content = content.replace(old_flagged_block, new_flagged_block)
    print("Updated Flagged for Action tab with Draft Reply feature.")
else:
    print("Flagged block not found - manual check needed.")

open(path, "w", encoding="utf-8").write(content)
