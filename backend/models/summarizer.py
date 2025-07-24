# ======= MINIMAL EDITS: Use consistent CSV names and columns ==========
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

DEVICE_ID = 0 if torch.cuda.is_available() else -1
DEVICE_NAME = "GPU" if DEVICE_ID >= 0 else "CPU"
MAX_OUTPUT_LENGTH = 200
MIN_OUTPUT_LENGTH = 10

def chunk_text(text: str, tokenizer, max_tokens: int):
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]
    chunks = []
    for i in range(0, len(input_ids), max_tokens):
        chunk_ids = input_ids[i : i + max_tokens]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunks.append(chunk_text)
    return chunks

# === BEGIN INTEGRATION: Consistent function and filenames ===
def summarize_reviews(labeled_csv='reviews_labeled.csv'):
    df = pd.read_csv(labeled_csv)
    model_name = "facebook/bart-large-cnn"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    max_tokens = model.config.max_position_embeddings
    tokenizer.model_max_length = max_tokens

    if DEVICE_ID >= 0:
        model.to("cuda")

    summarizer = pipeline(
        "summarization",
        model=model,
        tokenizer=tokenizer,
        device=DEVICE_ID
    )

    print(f"Using device for summarization: {DEVICE_NAME} (id={DEVICE_ID}); max_input_tokens={max_tokens}")

    def summarize_category(sent_val: int, label: str):
        reviews = df[df["sentiment"] == sent_val]["review_text"].astype(str).tolist()
        if not reviews:
            print(f"No {label} reviews to summarize.")
            return
        full_text = " ".join(reviews)
        text_chunks = chunk_text(full_text, tokenizer, max_tokens)
        summary_chunks = []
        for chunk in text_chunks:
            result = summarizer(
                chunk,
                max_length=MAX_OUTPUT_LENGTH,
                min_length=MIN_OUTPUT_LENGTH,
                truncation=True
            )
            summary_chunks.append(result[0]["summary_text"])
        combined_summary = " ".join(summary_chunks)
        print(f"\n=== {label} Reviews Summary ===\n{combined_summary}\n")

    summarize_category(1, "Positive")
    summarize_category(-1, "Negative")
# === END INTEGRATION ===

if __name__ == "__main__":
    summarize_reviews('reviews_labeled.csv')
