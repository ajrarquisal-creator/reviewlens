import pandas as pd
import re
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "reviews_small.csv")

REQUIRED_COLUMNS = ["Text", "Score"]


def load_dataset(path: str = DATA_PATH) -> pd.DataFrame:
    """Load the raw CSV into a DataFrame."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")
    df = pd.read_csv(path)
    return df


def validate_dataset(df: pd.DataFrame) -> None:
    """Ensure required columns exist."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")


def _clean_text(text: str) -> str:
    """Clean a single review's text."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataset: handle missing values, duplicates, and messy text."""
    df = df.copy()
    df = df[["Id", "Text", "Summary", "Score"]]
    df = df.dropna(subset=["Text", "Score"])
    df = df.drop_duplicates(subset=["Text"])
    df["Text"] = df["Text"].apply(_clean_text)
    df = df[df["Text"].str.len() > 0]
    df = df[df["Text"].str.len() >= 10]
    df = df.reset_index(drop=True)
    return df


def sample_dataset(df: pd.DataFrame, n: int = 100, random_state: int = 42) -> pd.DataFrame:
    """Randomly sample n rows to control API costs."""
    if len(df) <= n:
        return df
    return df.sample(n=n, random_state=random_state).reset_index(drop=True)