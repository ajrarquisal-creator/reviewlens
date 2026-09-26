path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict, aggregate_aspects"
new_import = "from src.genai_client import analyze_review, compute_priority, draft_reply, summarize_themes, is_conflict, aggregate_aspects, get_flag_reason"
content = content.replace(old_import, new_import)
print("import updated:", new_import in content)

old_flagged_loop = """            st.subheader("\u270D\uFE0F Draft Replies")
            for idx, row in flagged_df.reset_index(drop=True).iterrows():
                with st.expander(f"Review: {row[\x27Review\x27][:80]}..."):
                    st.write(f"**Sentiment:** {row[\x27AI Sentiment\x27]} | **Star Rating:** {row[\x27Star Rating\x27]}")
                    st.write(f"**Summary:** {row[\x27Summary\x27]}")
                    reply_key = f"reply_{idx}"
                    if st.button(f"\u270D\uFE0F Draft Reply", key=f"draft_btn_{idx}"):
                        with st.spinner("Drafting reply..."):
                            reply = draft_reply(row["Review"], row["AI Sentiment"])
                            st.session_state[reply_key] = reply
                    if reply_key in st.session_state:
                        st.text_area("Suggested reply", st.session_state[reply_key], key=f"reply_area_{idx}")"""

new_flagged_loop = """            st.subheader("\U0001F9ED Action Center")
            for idx, row in flagged_df.reset_index(drop=True).iterrows():
                with st.expander(f"Review: {row[\x27Review\x27][:80]}..."):
                    fake_analysis = {
                        "sentiment": row["AI Sentiment"],
                        "confidence": row["Confidence"],
                    }
                    flag_info = get_flag_reason(fake_analysis, row["Star Rating"], row["Priority"])

                    st.write(f"**Sentiment:** {row[\x27AI Sentiment\x27]} | **Star Rating:** {row[\x27Star Rating\x27]} | **Confidence:** {row[\x27Confidence\x27]:.0%}")
                    st.write(f"**Summary:** {row[\x27Summary\x27]}")
                    st.warning(f"**Why flagged:** {flag_info[\x27reason\x27]}")
                    st.info(f"**Suggested action:** {flag_info[\x27action\x27]}")

                    reply_key = f"reply_{idx}"
                    if st.button(f"\u270D\uFE0F Draft Reply", key=f"draft_btn_{idx}"):
                        with st.spinner("Drafting reply..."):
                            reply = draft_reply(row["Review"], row["AI Sentiment"])
                            st.session_state[reply_key] = reply
                    if reply_key in st.session_state:
                        st.text_area("Suggested reply", st.session_state[reply_key], key=f"reply_area_{idx}")"""

if old_flagged_loop in content:
    content = content.replace(old_flagged_loop, new_flagged_loop)
    print("Flagged loop updated: True")
else:
    print("Flagged loop updated: False - not found")

open(path, "w", encoding="utf-8").write(content)
