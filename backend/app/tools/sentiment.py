"""
tools/sentiment.py — Sentiment Analyzer
Base model: DistilBERT, fine-tuned on SST-2
Output: {label: "Positive"|"Negative", confidence: float}
"""

from __future__ import annotations

import logging
from typing import Any

import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

from app.config import MODEL_PATHS
from app.tools._loader import prepare_model_dir

logger = logging.getLogger(__name__)


class SentimentTool:
    id = "sentiment"
    display_name = "Sentiment Analyzer"
    description = "Tells you whether a piece of text is positive or negative."
    base_model = "DistilBERT"
    fine_tune_dataset = "SST-2"
    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "title": "Text",
                "description": "The text to analyse.",
                "minLength": 1,
                "maxLength": 5000,
            }
        },
    }

    def __init__(self) -> None:
        model_dir = prepare_model_dir(MODEL_PATHS["sentiment"])
        logger.info("Loading SentimentTool from %s", model_dir)
        self._tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
        self._model = DistilBertForSequenceClassification.from_pretrained(model_dir)
        self._model.eval()
        logger.info("SentimentTool ready")

    def predict(self, *, text: str, **_: Any) -> dict[str, Any]:
        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.no_grad():
            logits = self._model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        idx = int(probs.argmax())
        label_map = self._model.config.id2label
        raw_label = str(label_map.get(idx, idx)).upper()
        # SST-2 fine-tuned checkpoints may use NEGATIVE/POSITIVE or LABEL_0/LABEL_1 or 0/1
        label = "Positive" if raw_label in ("1", "POSITIVE", "LABEL_1") else "Negative"
        return {"label": label, "confidence": round(float(probs[idx]), 4)}
