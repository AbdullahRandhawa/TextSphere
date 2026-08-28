"""
tools/qa.py — Question Answering
Base model: DistilBERT, fine-tuned on SQuAD v1.1
Input: {question, context}  — two distinct required fields
Output: {answer: str, confidence: float}
"""

from __future__ import annotations

import logging
from typing import Any

import torch
from transformers import DistilBertForQuestionAnswering, DistilBertTokenizerFast

from app.config import MODEL_PATHS
from app.tools._loader import prepare_model_dir

logger = logging.getLogger(__name__)


class QaTool:
    id = "qa"
    display_name = "Question Answering"
    description = "Answers a specific question using a passage you provide as context."
    base_model = "DistilBERT"
    fine_tune_dataset = "SQuAD v1.1"
    input_schema = {
        "type": "object",
        "required": ["question", "context"],
        "properties": {
            "question": {
                "type": "string",
                "title": "Question",
                "description": "The question to answer.",
                "minLength": 1,
                "maxLength": 1000,
                "x-ui-widget": "input",
            },
            "context": {
                "type": "string",
                "title": "Context",
                "description": "The passage that contains the answer.",
                "minLength": 10,
                "maxLength": 10000,
                "x-ui-widget": "textarea",
            },
        },
    }

    def __init__(self) -> None:
        model_dir = prepare_model_dir(MODEL_PATHS["qa"])
        logger.info("Loading QaTool from %s", model_dir)
        self._tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
        self._model = DistilBertForQuestionAnswering.from_pretrained(model_dir)
        self._model.eval()
        logger.info("QaTool ready")

    def predict(self, *, question: str, context: str, **_: Any) -> dict[str, Any]:
        inputs = self._tokenizer(
            question,
            context,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            return_offsets_mapping=True,
        )
        offset_mapping = inputs.pop("offset_mapping")[0]
        sequence_ids = inputs.sequence_ids(0)

        with torch.no_grad():
            outputs = self._model(**inputs)

        start_logits = outputs.start_logits[0]
        end_logits   = outputs.end_logits[0]

        # Mask question tokens and special tokens — only score context positions
        start_scores = start_logits.clone()
        end_scores   = end_logits.clone()
        for i, sid in enumerate(sequence_ids):
            if sid != 1:
                start_scores[i] = float("-inf")
                end_scores[i]   = float("-inf")

        start_idx = int(start_scores.argmax())
        end_idx   = int(end_scores.argmax())
        if end_idx < start_idx:
            end_idx = start_idx

        char_start = int(offset_mapping[start_idx][0])
        char_end   = int(offset_mapping[end_idx][1])
        answer = context[char_start:char_end].strip()

        start_conf = float(torch.softmax(start_logits, dim=0)[start_idx])
        end_conf   = float(torch.softmax(end_logits,   dim=0)[end_idx])
        confidence = round((start_conf + end_conf) / 2, 4)

        return {"answer": answer or "[No answer found]", "confidence": confidence}
