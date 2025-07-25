import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Use GPU if available, otherwise CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define a clear mapping from model labels to sentiment names
SENTIMENT_MAP = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive",
}

class SentimentModel:
    """
    A class to load the sentiment analysis model and make predictions.
    This ensures the model is loaded into memory only once.
    """
    def __init__(self):
        self.tokenizer = None
        self.model = None

    def load(self):
        """Loads the tokenizer and model from Hugging Face."""
        print("Loading sentiment analysis model...")
        model_name = "cardiffnlp/twitter-roberta-base-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(DEVICE)
        self.model.eval() # Set the model to evaluation mode
        print(f"Sentiment model loaded successfully on {DEVICE}.")

    def predict(self, text: str):
        """Analyzes a single piece of text and returns the sentiment."""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model is not loaded. Call load() before predict().")

        # Tokenize the text and move tensors to the correct device
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        # Make a prediction
        with torch.no_grad():
            logits = self.model(**inputs).logits

        # Get probabilities and the predicted label
        probabilities = torch.softmax(logits, dim=-1)
        confidence, predicted_class_id = torch.max(probabilities, dim=-1)

        # Map the prediction to a sentiment label
        label_str = self.model.config.id2label[predicted_class_id.item()]
        sentiment = SENTIMENT_MAP.get(label_str, "Neutral")

        return {
            "sentiment": sentiment,
            "confidence": round(confidence.item() * 100, 2)
        }

# Create a single instance that your FastAPI app will use
sentiment_analyzer = SentimentModel()