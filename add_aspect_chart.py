path = "src/visualize.py"
content = open(path, "r", encoding="utf-8").read()

new_function = """

def aspect_breakdown_chart(aspect_summary: dict):
    \"\"\"Stacked bar chart of aspect mentions by sentiment.\"\"\"
    rows = []
    for aspect, counts in aspect_summary.items():
        for sentiment in ["positive", "neutral", "negative"]:
            if counts.get(sentiment, 0) > 0:
                rows.append({"Aspect": aspect.title(), "Sentiment": sentiment, "Count": counts[sentiment]})

    if not rows:
        return None

    df = pd.DataFrame(rows)
    aspect_order = (
        df.groupby("Aspect")["Count"].sum().sort_values(ascending=False).index.tolist()
    )

    color_map = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}

    fig = px.bar(
        df,
        x="Aspect",
        y="Count",
        color="Sentiment",
        color_discrete_map=color_map,
        title="Most-Mentioned Aspects by Sentiment",
        barmode="stack",
        category_orders={"Aspect": aspect_order},
    )
    return fig
"""

if "def aspect_breakdown_chart" in content:
    print("already exists")
else:
    content = content.rstrip() + "\n" + new_function
    open(path, "w", encoding="utf-8").write(content)
    print("Added aspect_breakdown_chart.")
