"""
tools/topic.py — Topic Classifier
Base model: DistilBERT, fine-tuned on AG News
Output: {label: "World"|"Sports"|"Business"|"Sci/Tech", confidence: float}
"""

from __future__ import annotations

import logging
from typing import Any

import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

from app.config import MODEL_PATHS
from app.tools._loader import prepare_model_dir

logger = logging.getLogger(__name__)

# AG News label order (0-indexed): World, Sports, Business, Sci/Tech
_AG_NEWS_LABELS = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}


class TopicTool:
    id = "topic"
    display_name = "Topic Classifier"
    description = "Sorts text into a news category: World, Sports, Business, or Sci/Tech."
    base_model = "DistilBERT"
    fine_tune_dataset = "AG News"
    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "title": "Text",
                "description": "The text to classify.",
                "minLength": 1,
                "maxLength": 5000,
            }
        },
    }

    def __init__(self) -> None:
        model_dir = prepare_model_dir(MODEL_PATHS["topic"])
        logger.info("Loading TopicTool from %s", model_dir)
        self._tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
        self._model = DistilBertForSequenceClassification.from_pretrained(model_dir)
        self._model.eval()
        logger.info("TopicTool ready")

    def predict(self, *, text: str, **_: Any) -> dict[str, Any]:
        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.no_grad():
            logits = self._model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        idx = int(probs.argmax())
        # Prefer model's own id2label; fall back to AG News standard order
        label_map = getattr(self._model.config, "id2label", {})
        raw = str(label_map.get(idx, idx))
        label = _AG_NEWS_LABELS.get(idx, raw)
        return {"label": label, "confidence": round(float(probs[idx]), 4)}
