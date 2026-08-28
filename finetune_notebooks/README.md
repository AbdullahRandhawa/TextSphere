# Fine-Tuning Notebooks

This folder contains the Jupyter/Colab notebooks used to fine-tune the models powering TextSphere's NLP tools.

## Models & Notebooks

| Tool | Base Model | Dataset | Notebook |
|------|-----------|---------|----------|
| Sentiment Analysis | DistilBERT | SST-2 | `sentiment_finetune.ipynb` |
| Topic Classification | DistilBERT | AG News | `topic_finetune.ipynb` |
| Named Entity Recognition | BERT | CoNLL-2003 | `ner_finetune.ipynb` |
| Summarization | T5-small | CNN/DailyMail | `summarization_finetune.ipynb` |
| Question Answering | DistilBERT | SQuAD | `qa_finetune.ipynb` |

## How to Use

These notebooks are designed to run on **Google Colab** (free GPU).

1. Open the notebook in Colab
2. Enable GPU: Runtime → Change runtime type → T4 GPU
3. Run all cells
4. Download the output model folder when training is complete
5. Place the folder in `backend/app/finetuned_models/<tool_name>/`

## Pre-trained Checkpoints

The fine-tuned model weights are **not stored in this repo** (too large for GitHub).

Download the pre-trained checkpoints via:

```bash
pip install gdown
python download_models.py
```

> You must configure the Google Drive folder IDs in `download_models.py` first.
> See that file's comments for step-by-step instructions.
