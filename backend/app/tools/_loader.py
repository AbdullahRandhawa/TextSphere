"""
tools/_loader.py — Maps checkpoint files with '(1)' in their names to the
standard HuggingFace filename convention by copying them into a temp directory.

Windows file symlinks require admin privileges, so we use shutil.copy2 directly.
The temp directory is cached per model dir for the process lifetime.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Standard filename aliases — maps every known non-standard name to the
# standard HuggingFace filename expected by from_pretrained().
_RENAME_MAP: dict[str, str] = {
    # Files WITH the (1) suffix (your fine-tuned checkpoints)
    "config (1).json":           "config.json",
    "model (1).safetensors":     "model.safetensors",
    "tokenizer (1).json":        "tokenizer.json",
    "tokenizer_config (1).json": "tokenizer_config.json",
    "tokenizer_config (1).json": "tokenizer_config.json",
    "training_args (1).bin":     "training_args.bin",
    "vocab (1).txt":             "vocab.txt",
    "merges (1).txt":            "merges.txt",
    "special_tokens_map (1).json": "special_tokens_map.json",
    "spiece (1).model":          "spiece.model",
    # Already-standard names (copy as-is)
    "config.json":               "config.json",
    "model.safetensors":         "model.safetensors",
    "tokenizer.json":            "tokenizer.json",
    "tokenizer_config.json":     "tokenizer_config.json",
    "training_args.bin":         "training_args.bin",
    "vocab.txt":                 "vocab.txt",
    "merges.txt":                "merges.txt",
    "special_tokens_map.json":   "special_tokens_map.json",
    "spiece.model":              "spiece.model",
    "generation_config.json":    "generation_config.json",
    "sentencepiece.bpe.model":   "sentencepiece.bpe.model",
}

# Process-lifetime cache: source_dir → temp dir path
_TEMP_CACHE: dict[Path, str] = {}


def prepare_model_dir(source_dir: Path) -> str:
    """
    Return a path to a temp directory where all checkpoint files use standard
    HuggingFace names.  Results are cached for the process lifetime.

    Raises FileNotFoundError if source_dir does not exist.
    """
    if source_dir in _TEMP_CACHE:
        return _TEMP_CACHE[source_dir]

    if not source_dir.exists():
        raise FileNotFoundError(
            f"Model directory not found: {source_dir}\n"
            "Make sure the fine-tuned model folder exists at that path.\n"
            "Check backend/app/finetuned_models/ and the directory junctions."
        )

    tmp = tempfile.mkdtemp(prefix=f"ts_{source_dir.name}_")
    logger.info("Staging model files from '%s' -> '%s'", source_dir.name, tmp)

    copied = 0
    for src_file in source_dir.iterdir():
        if not src_file.is_file():
            continue
        dest_name = _RENAME_MAP.get(src_file.name, src_file.name)
        dest_path = Path(tmp) / dest_name
        # Skip if already staged (handles duplicates in the rename map)
        if dest_path.exists():
            continue
        shutil.copy2(str(src_file), str(dest_path))
        copied += 1

    logger.info("Staged %d files for model '%s'", copied, source_dir.name)
    _TEMP_CACHE[source_dir] = tmp
    return tmp
