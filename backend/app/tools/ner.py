"""
tools/ner.py — Named Entity Recognizer
Base model: BERT, fine-tuned on CoNLL-2003
Output: {entities: [{text, label, start, end}]}

B-/I- tags are merged into whole-mention spans before returning.
"""

from __future__ import annotations

import logging
from typing import Any

import torch
from transformers import BertForTokenClassification, BertTokenizerFast

from app.config import MODEL_PATHS
from app.tools._loader import prepare_model_dir

logger = logging.getLogger(__name__)


class NerTool:
    id = "ner"
    display_name = "Named Entity Recognizer"
    description = "Finds people, organizations, and locations mentioned in your text."
    base_model = "BERT"
    fine_tune_dataset = "CoNLL-2003"
    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "title": "Text",
                "description": "The text to scan for named entities.",
                "minLength": 1,
                "maxLength": 5000,
            }
        },
    }

    def __init__(self) -> None:
        model_dir = prepare_model_dir(MODEL_PATHS["ner"])
        logger.info("Loading NerTool from %s", model_dir)
        self._tokenizer = BertTokenizerFast.from_pretrained(model_dir)
        self._model = BertForTokenClassification.from_pretrained(model_dir)
        self._model.eval()
        logger.info("NerTool ready")

    def predict(self, *, text: str, **_: Any) -> dict[str, Any]:
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            return_offsets_mapping=True,
        )
        offset_mapping = inputs.pop("offset_mapping")[0].tolist()
        sequence_ids = inputs.sequence_ids(0)

        with torch.no_grad():
            logits = self._model(**inputs).logits
        predictions = torch.argmax(logits, dim=-1)[0].tolist()

        id2label = self._model.config.id2label
        entities: list[dict] = []
        current: dict | None = None

        for i, (pred, (start, end)) in enumerate(zip(predictions, offset_mapping)):
            # Skip special tokens ([CLS], [SEP], padding)
            if sequence_ids[i] is None:
                if current:
                    entities.append(current)
                    current = None
                continue
            if start == end:
                continue

            label = id2label.get(pred, "O")
            if label == "O":
                if current:
                    entities.append(current)
                    current = None
            elif label.startswith("B-"):
                if current:
                    entities.append(current)
                entity_type = label[2:]
                current = {
                    "text": text[start:end],
                    "label": entity_type,
                    "start": start,
                    "end": end,
                }
            elif label.startswith("I-") and current:
                # Extend the current span
                current["text"] = text[current["start"]: end]
                current["end"] = end
            else:
                if current:
                    entities.append(current)
                    current = None

        if current:
            entities.append(current)

        return {"entities": entities}
