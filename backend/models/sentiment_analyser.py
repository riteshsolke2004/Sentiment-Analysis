# ====== MINIMAL EDITS: Fix CSV filenames and review text column =======

import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm.auto import tqdm

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

LABEL_MAP = {
    "LABEL_0": -1,
    "LABEL_1": 0,
    "LABEL_2": 1,
}

def map_label(label_str: str) -> int:
    return LABEL_MAP.get(label_str, 0)

# === BEGIN INTEGRATION: rework for consistent filename and function ===
def annotate_sentiments(input_csv='reviews.csv', output_csv='reviews_labeled.csv'):
    """
    Annotate review sentiment and save as reviews_labeled.csv
    """
    df = pd.read_csv(input_csv)   # expects 'review_text' column
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.to(DEVICE)
    model.eval()
    labels = []
    for text in tqdm(df["review_text"].astype(str), desc="Classifying"):
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256
        )
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        with torch.no_grad():
            logits = model(**inputs).logits
        pred = logits.softmax(dim=-1).argmax().item()
        label_str = model.config.id2label[pred]
        labels.append(map_label(label_str))
    df["sentiment"] = labels
    df.to_csv(output_csv, index=False)
    print(f"Saved {output_csv} with sentiment labels on {DEVICE}.")

# === END INTEGRATION ===

if __name__ == "__main__":
    # Default CLI usage, consistent filenames
    annotate_sentiments('reviews.csv', 'reviews_labeled.csv')
