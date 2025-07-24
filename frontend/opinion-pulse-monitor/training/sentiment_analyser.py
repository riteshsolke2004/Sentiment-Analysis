import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm.auto import tqdm

# Detect device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Map cardiffnlp/twitter-roberta-base-sentiment labels to sentiment values
# config.id2label: {0: 'LABEL_0', 1: 'LABEL_1', 2: 'LABEL_2'}
# We treat LABEL_0 = Negative (-1), LABEL_1 = Neutral (0), LABEL_2 = Positive (+1)
LABEL_MAP = {
    "LABEL_0": -1,
    "LABEL_1": 0,
    "LABEL_2": 1,
}

def map_label(label_str: str) -> int:
    return LABEL_MAP.get(label_str, 0)


def main():
    # Load scraped reviews
    df = pd.read_csv("./training/dataset/test2.csv")  # expects a column "review"
    
    # Load pretrained RoBERTa classifier
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.to(DEVICE)
    model.eval()
    
    # Classify each review
    labels = []
    for text in tqdm(df["review"].astype(str), desc="Classifying"):
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
    
    # Save labeled reviews
    df["sentiment"] = labels
    df.to_csv("./training/dataset/test.csv", index=False)
    print(f"Saved reviews_labeled.csv with sentiment labels on {DEVICE}.")

if __name__ == "__main__":
    main()