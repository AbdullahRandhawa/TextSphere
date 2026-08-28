"""
tools/summarization.py — Text Summarizer
Base model: T5-small, fine-tuned on CNN/DailyMail
Output: {summary: str}
"""

from __future__ import annotations

import logging
from typing import Any

import torch
from transformers import T5ForConditionalGeneration, T5TokenizerFast

from app.config import MODEL_PATHS
from app.tools._loader import prepare_model_dir

logger = logging.getLogger(__name__)

_DEFAULT_MAX_LENGTH = 150
_DEFAULT_MIN_LENGTH = 40


class SummarizationTool:
    id = "summarization"
    display_name = "Text Summarizer"
    description = "Condenses a long passage into a short summary."
    base_model = "T5-small"
    fine_tune_dataset = "CNN/DailyMail"
    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "title": "Text",
                "description": "The passage to summarise (min 50 chars).",
                "minLength": 50,
                "maxLength": 10000,
            },
            "max_length": {
                "type": "integer",
                "title": "Max summary length (tokens)",
                "default": _DEFAULT_MAX_LENGTH,
                "minimum": 20,
                "maximum": 500,
            },
            "min_length": {
                "type": "integer",
                "title": "Min summary length (tokens)",
                "default": _DEFAULT_MIN_LENGTH,
                "minimum": 10,
                "maximum": 200,
            },
        },
    }

    def __init__(self) -> None:
        model_dir = prepare_model_dir(MODEL_PATHS["summarization"])
        logger.info("Loading SummarizationTool from %s", model_dir)
        self._tokenizer = T5TokenizerFast.from_pretrained(model_dir)
        self._model = T5ForConditionalGeneration.from_pretrained(model_dir)
        self._model.eval()
        logger.info("SummarizationTool ready")

    def predict(
        self,
        *,
        text: str,
        max_length: int = _DEFAULT_MAX_LENGTH,
        min_length: int = _DEFAULT_MIN_LENGTH,
        **_: Any,
    ) -> dict[str, Any]:
        # T5 requires a task prefix
        inputs = self._tokenizer(
            "summarize: " + text,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )
        with torch.no_grad():
            output_ids = self._model.generate(
                **inputs,
                max_length=int(max_length),
                min_length=int(min_length),
                num_beams=4,
                early_stopping=True,
            )
        summary = self._tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return {"summary": summary}
