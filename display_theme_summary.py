path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_overview_start = """    with tab_overview:
        m1, m2, m3, m4 = st.columns(4)"""

new_overview_start = """    with tab_overview:
        if "theme_summary" in st.session_state:
            theme = st.session_state["theme_summary"]
            with st.container(border=True):
                st.subheader("\U0001F4A1 Key Themes")
                st.write(f"**Overall takeaway:** {theme.get(\x27overall_takeaway\x27, \x27N/A\x27)}")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**\u2705 Top Praises**")
                    for p in theme.get("top_praises", []):
                        st.markdown(f"- {p}")
                with col_b:
                    st.markdown("**\u26A0\uFE0F Top Complaints**")
                    for c in theme.get("top_complaints", []):
                        st.markdown(f"- {c}")

        m1, m2, m3, m4 = st.columns(4)"""

if old_overview_start in content:
    content = content.replace(old_overview_start, new_overview_start)
    print("Added theme summary display to Overview tab.")
else:
    print("Overview tab start not found - manual check needed.")

open(path, "w", encoding="utf-8").write(content)
