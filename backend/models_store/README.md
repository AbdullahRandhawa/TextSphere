# models_store/

This directory is the spec-defined location for fine-tuned model artifacts.

For this project, model weights are stored in the workspace root (alongside
`backend/`) in their original folder names:

  - `distilbert_sst2/`             → Sentiment Analyzer
  - `distilbert_agnews/`           → Topic Classifier
  - `bert_conll2003_ner/`          → Named Entity Recognizer
  - `t5_cnn_dailymail_summarization/` → Text Summarizer
  - `distilbert_squad_qa/`         → Question Answering

The `config.py` maps each tool ID to the correct workspace-root folder.
You do not need to place anything inside this directory.
