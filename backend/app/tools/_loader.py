"""
tools/_loader.py — Resolves model directories for from_pretrained().

All files in finetuned_models/ now use standard HuggingFace filenames
(config.json, model.safetensors, tokenizer.json, etc.) so we can load
directly from the source directory without any temp-copy step.

The prepare_model_dir() function is kept as the single entry point so
callers (sentiment.py, ner.py, etc.) don't need to change.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Process-lifetime cache: source_dir → resolved path string
_DIR_CACHE: dict[Path, str] = {}


def prepare_model_dir(source_dir: Path) -> str:
    """
    Return the path to the model directory ready for from_pretrained().

    Raises FileNotFoundError if source_dir does not exist or contains
    no .safetensors weight file.
    """
    if source_dir in _DIR_CACHE:
        return _DIR_CACHE[source_dir]

    if not source_dir.exists():
        raise FileNotFoundError(
            f"Model directory not found: {source_dir}\n"
            "Make sure you have run:  python download_models.py\n"
            "or manually placed the model files in that directory."
        )

    # Verify at least one weight file is present
    weights = list(source_dir.glob("*.safetensors"))
    if not weights:
        raise FileNotFoundError(
            f"No .safetensors weight file found in: {source_dir}\n"
            "The directory exists but appears empty or incomplete.\n"
            "Re-run download_models.py or re-copy the model files."
        )

    resolved = str(source_dir.resolve())
    logger.info("Model '%s' -> %s", source_dir.name, resolved)
    _DIR_CACHE[source_dir] = resolved
    return resolved

