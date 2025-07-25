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
class SentimentModel:
    def __init__(self):
        self.tokenizer = None
        self.model = None
    def load(self):
        model_name = "cardiffnlp/twitter-roberta-base-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(DEVICE)
        self.model.eval() # Set the model to evaluation mode
        print(f"Sentiment model loaded successfully on {DEVICE}.")
    def map_label(self, label_str: str) -> int:
        return LABEL_MAP.get(label_str, 0)

# === BEGIN INTEGRATION: rework for consistent filename and function ===
    def annotate_sentiments(self, input_csv='./data/reviews.csv', output_csv='./data/reviews_labeled.csv'):
        """
        Annotate review sentiment and save as reviews_labeled.csv
        """
        df = pd.read_csv(input_csv)   # expects 'review_text' column
        
        labels = []
        for text in tqdm(df["review_text"].astype(str), desc="Classifying"):
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256
            )
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probabilities = torch.softmax(logits, dim=-1)
            confidence, predicted_class_id = torch.max(probabilities, dim=-1)

            pred = logits.softmax(dim=-1).argmax().item()
            label_str = self.model.config.id2label[pred]
            labels.append(self.map_label(label_str))
        df["sentiment"] = labels
        df.to_csv(output_csv, index=False)
        print(f"Saved {output_csv} with sentiment labels on {DEVICE}.")
        return {
            "sentiment": labels,
            "confidence": round(confidence.item() * 100, 2)
        }

# === END INTEGRATION ===


