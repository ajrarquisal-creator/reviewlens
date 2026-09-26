path = "app.py"
content = open(path, "r", encoding="utf-8").read()

helper_code = """
def style_results(df):
    def color_sentiment(val):
        colors = {"positive": "#D1FADF", "negative": "#FEE4E2", "neutral": "#F2F4F7", "unknown": "#FEF0C7"}
        return f"background-color: {colors.get(val, '''')}"

    def color_priority(val):
        colors = {"High": "#FEE4E2", "Medium": "#FEF0C7", "Low": "#D1FADF"}
        return f"background-color: {colors.get(val, '''')}"

    styler = df.style
    if "AI Sentiment" in df.columns:
        styler = styler.map(color_sentiment, subset=["AI Sentiment"])
    if "Priority" in df.columns:
        styler = styler.map(color_priority, subset=["Priority"])
    return styler

"""

marker = "st.set_page_config(page_title=\"ReviewLens\", page_icon=\"\U0001F50D\", layout=\"wide\")"

if "def style_results" in content:
    print("style_results already exists - skipping insertion.")
else:
    content = content.replace(marker, helper_code + marker, 1)
    print("Inserted style_results helper.")

old_queue_line = "st.dataframe(filtered.drop(columns=[\"Error\"]), use_container_width=True)"
new_queue_line = "st.dataframe(style_results(filtered.drop(columns=[\"Error\"])), use_container_width=True)"
if old_queue_line in content:
    content = content.replace(old_queue_line, new_queue_line)
    print("Updated Review Queue dataframe call.")
else:
    print("Review Queue dataframe line not found - may already be updated.")

old_flagged_line = "st.dataframe(flagged_df, use_container_width=True)"
new_flagged_line = "st.dataframe(style_results(flagged_df), use_container_width=True)"
if old_flagged_line in content:
    content = content.replace(old_flagged_line, new_flagged_line)
    print("Updated Flagged for Action dataframe call.")
else:
    print("Flagged for Action dataframe line not found - may already be updated.")

open(path, "w", encoding="utf-8").write(content)
print("Done - app.py saved.")
