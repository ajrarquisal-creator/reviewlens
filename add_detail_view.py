path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_queue_block = """        st.dataframe(style_results(filtered.drop(columns=["Error"])), use_container_width=True)
        st.caption(f"Showing {len(filtered)} of {len(results_df)} analyzed reviews.")

        csv_data = filtered.drop(columns=["Error"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            "\u2B07\uFE0F Export queue to CSV",
            data=csv_data,
            file_name="reviewlens_results.csv",
            mime="text/csv",
        )"""

new_queue_block = """        display_cols = [c for c in filtered.columns if c not in ("Error", "Full Review", "Aspects")]
        st.dataframe(style_results(filtered[display_cols]), use_container_width=True)
        st.caption(f"Showing {len(filtered)} of {len(results_df)} analyzed reviews.")

        csv_data = filtered[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "\u2B07\uFE0F Export queue to CSV",
            data=csv_data,
            file_name="reviewlens_results.csv",
            mime="text/csv",
        )

        st.divider()
        st.subheader("\U0001F4C4 Review Detail View")
        if filtered.empty:
            st.info("No reviews match the current filters.")
        else:
            options = filtered.index.tolist()
            selected_idx = st.selectbox(
                "Select a review to inspect",
                options=options,
                format_func=lambda i: f"#{i}: {filtered.loc[i, \x27Review\x27][:60]}...",
            )
            detail = filtered.loc[selected_idx]

            with st.container(border=True):
                st.write(f"**Full Review:** {detail[\x27Full Review\x27]}")
                d1, d2, d3 = st.columns(3)
                d1.metric("Star Rating", f"{detail[\x27Star Rating\x27]}\u2B50")
                d2.metric("AI Sentiment", detail["AI Sentiment"])
                d3.metric("Confidence", f"{detail[\x27Confidence\x27]:.0%}")
                st.write(f"**Priority:** {detail[\x27Priority\x27]}")
                st.write(f"**Keywords:** {detail[\x27Keywords\x27]}")
                st.write(f"**Summary:** {detail[\x27Summary\x27]}")

                aspects = detail.get("Aspects", [])
                if aspects:
                    st.write("**Aspects mentioned:**")
                    for a in aspects:
                        st.markdown(f"- {a.get(\x27aspect\x27, \x27?\x27).title()}: {a.get(\x27sentiment\x27, \x27?\x27)}")

                detail_reply_key = f"detail_reply_{selected_idx}"
                if st.button("\u270D\uFE0F Draft Reply for this review", key=f"detail_draft_btn_{selected_idx}"):
                    with st.spinner("Drafting reply..."):
                        reply = draft_reply(detail["Full Review"], detail["AI Sentiment"])
                        st.session_state[detail_reply_key] = reply
                if detail_reply_key in st.session_state:
                    st.text_area("Suggested reply", st.session_state[detail_reply_key], key=f"detail_reply_area_{selected_idx}")"""

if old_queue_block in content:
    content = content.replace(old_queue_block, new_queue_block)
    print("Review Queue detail view added: True")
else:
    print("Review Queue detail view added: False - not found")

open(path, "w", encoding="utf-8").write(content)
