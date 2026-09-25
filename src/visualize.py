import plotly.express as px
import pandas as pd


def sentiment_distribution_chart(df: pd.DataFrame):
    """Bar chart of sentiment counts."""
    counts = df["AI Sentiment"].value_counts().reset_index()
    counts.columns = ["Sentiment", "Count"]

    color_map = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c", "unknown": "#f39c12"}

    fig = px.bar(
        counts,
        x="Sentiment",
        y="Count",
        color="Sentiment",
        color_discrete_map=color_map,
        title="Sentiment Distribution",
        text="Count",
    )
    fig.update_layout(showlegend=False)
    return fig


def confidence_distribution_chart(df: pd.DataFrame):
    """Histogram of confidence scores."""
    fig = px.histogram(
        df,
        x="Confidence",
        nbins=20,
        title="AI Confidence Score Distribution",
        color_discrete_sequence=["#3498db"],
    )
    fig.update_layout(bargap=0.1)
    return fig


def rating_vs_sentiment_chart(df: pd.DataFrame):
    """
    Compares star rating to AI sentiment to surface disagreements
    (e.g. a 5-star review the AI flagged as negative).
    """
    grouped = df.groupby(["Star Rating", "AI Sentiment"]).size().reset_index(name="Count")

    color_map = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c", "unknown": "#f39c12"}

    fig = px.bar(
        grouped,
        x="Star Rating",
        y="Count",
        color="AI Sentiment",
        color_discrete_map=color_map,
        title="Star Rating vs AI Sentiment (spot the disagreements)",
        barmode="stack",
    )
    return fig
def priority_distribution_chart(df: pd.DataFrame):
    """Bar chart of how many reviews fall into each priority tier."""
    counts = df["Priority"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0).reset_index()
    counts.columns = ["Priority", "Count"]

    color_map = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"}

    fig = px.bar(
        counts,
        x="Priority",
        y="Count",
        color="Priority",
        color_discrete_map=color_map,
        title="Reviews by Action Priority",
        text="Count",
        category_orders={"Priority": ["High", "Medium", "Low"]},
    )
    fig.update_layout(showlegend=False)
    return fig
