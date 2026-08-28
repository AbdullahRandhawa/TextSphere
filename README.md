# TextSphere

A full-stack AI-powered text analysis app. Users can chat with an LLM and run specialized NLP tools — Sentiment Analysis, Topic Classification, Named Entity Recognition, Summarization, and Question Answering — all powered by locally-served fine-tuned models.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Auth & DB | Firebase (Auth + Firestore) |
| LLM | OpenRouter API |
| NLP Models | HuggingFace Transformers (local inference) |

---

## Project Structure

```
TextSphere/
├── backend/                    # FastAPI server
│   ├── app/
│   │   ├── finetuned_models/   # ⚠️ Not in git — download separately
│   │   │   ├── sentiment/
│   │   │   ├── topic/
│   │   │   ├── ner/
│   │   │   ├── summarization/
│   │   │   └── qa/
│   │   ├── tools/              # NLP tool implementations
│   │   ├── api/                # API routes
│   │   ├── firebase/           # Auth + Firestore
│   │   ├── llm/                # OpenRouter client
│   │   ├── config.py
│   │   └── main.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/                   # React + Vite app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── hooks/
│   ├── .env.example
│   └── package.json
├── finetune_notebooks/         # Colab notebooks used to train the models
├── download_models.py          # Script to download models from Google Drive
├── setup_check.py              # Verify your environment before starting
└── README.md
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/AbdullahRandhawa/TextSphere.git
cd TextSphere
```

### 2. Download the fine-tuned models

The model weights are stored on Google Drive (too large for GitHub).

```bash
pip install gdown
python download_models.py
```

> If you're setting this up fresh, open `download_models.py` and paste in the Google Drive folder IDs.

### 3. Configure environment variables

**Backend:**
```bash
cp backend/.env.example backend/.env
# Fill in: OPENROUTER_API_KEY, FIREBASE_CREDENTIALS_PATH
```

**Frontend:**
```bash
cp frontend/.env.example frontend/.env
# Fill in: VITE_FIREBASE_API_KEY and other VITE_FIREBASE_* values
```

Also place your Firebase service-account JSON at `backend/firebase_credentials.json`.

### 4. Run the setup check

```bash
python setup_check.py
```

All checks should pass before starting.

### 5. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at **http://localhost:5173**

---

## NLP Tools

| Tool | Base Model | Fine-tuned On |
|------|-----------|---------------|
| Sentiment Analysis | DistilBERT | SST-2 |
| Topic Classification | DistilBERT | AG News |
| Named Entity Recognition | BERT | CoNLL-2003 |
| Summarization | T5-small | CNN/DailyMail |
| Question Answering | DistilBERT | SQuAD |

See [`finetune_notebooks/`](./finetune_notebooks/) for the training notebooks.

---

## Fine-Tuning

Notebooks for training each model are in the [`finetune_notebooks/`](./finetune_notebooks/) directory.
They are designed to run on **Google Colab** with a free T4 GPU.