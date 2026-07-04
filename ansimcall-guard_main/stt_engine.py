from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

LABELS = ["기관사칭", "금전요구", "긴급압박", "가족사칭", "개인정보", "앱설치유도", "가입유도"]

class KoBERTMultiLabelPredictor:
    def __init__(self, model_dir="models/kobert_multilabel"):
        self.model_dir = Path(model_dir)
        self.available = False
        self.error = None
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if self._has_model():
            self._load()

    def _has_model(self):
        if not self.model_dir.exists():
            return False
        names = {p.name for p in self.model_dir.iterdir()}
        return "config.json" in names and ("pytorch_model.bin" in names or "model.safetensors" in names)

    def _load(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir), trust_remote_code=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(str(self.model_dir), trust_remote_code=True).to(self.device)
            self.model.eval()
            self.available = True
        except Exception as e:
            self.error = str(e)
            self.available = False

    def predict(self, text: str, threshold=0.5):
        if not self.available:
            return {
                "available": False,
                "error": self.error,
                "label_probs": {},
                "predicted_labels": [],
            }

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256, padding=True).to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits.squeeze()
            probs = torch.sigmoid(logits).detach().cpu().tolist()

        label_probs = {label: round(float(prob), 4) for label, prob in zip(LABELS, probs)}
        predicted = [label for label, prob in label_probs.items() if prob >= threshold]

        return {
            "available": True,
            "error": None,
            "label_probs": label_probs,
            "predicted_labels": predicted,
        }
