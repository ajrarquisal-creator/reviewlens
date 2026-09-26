path = "app.py"
content = open(path, "r", encoding="utf-8").read()

old_append = """        results.append({
            "Review": row.Text[:150] + ("..." if len(row.Text) > 150 else ""),
            "Star Rating": row.Score,
            "AI Sentiment": analysis.get("sentiment", "unknown"),
            "Confidence": analysis.get("confidence", 0.0),
            "Priority": priority,
            "Keywords": ", ".join(analysis.get("keywords", [])),
            "Summary": analysis.get("summary", ""),
            "Error": analysis.get("error", False),
        })"""

new_append = """        results.append({
            "Review": row.Text[:150] + ("..." if len(row.Text) > 150 else ""),
            "Full Review": row.Text,
            "Star Rating": row.Score,
            "AI Sentiment": analysis.get("sentiment", "unknown"),
            "Confidence": analysis.get("confidence", 0.0),
            "Priority": priority,
            "Keywords": ", ".join(analysis.get("keywords", [])),
            "Summary": analysis.get("summary", ""),
            "Aspects": analysis.get("aspects", []),
            "Error": analysis.get("error", False),
        })"""

content = content.replace(old_append, new_append)
print("results append updated:", "Full Review" in content)

open(path, "w", encoding="utf-8").write(content)
