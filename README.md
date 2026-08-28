# 🌐 TextSphere — Intelligent Multi-Model NLP & LLM Workspace

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)

**TextSphere** is an end-to-end, full-stack Natural Language Processing (NLP) platform that merges the power of **locally-served, custom fine-tuned transformer models** with **cloud-based Large Language Models (LLMs)** via OpenRouter.

Users can engage in natural conversational AI while triggering specialized, fine-tuned transformer tools for specific NLP tasks — complete with real-time SSE streaming commentary, confidence metrics, and chat history persistence.

---

## 📑 Table of Contents

- [Features](#-features)
- [NLP Models & Datasets](#-nlp-models--datasets)
- [How to Get the Models](#-how-to-get-the-models)
- [Fine-Tuning Models on Your Own](#-fine-tuning-models-on-your-own)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Getting Started & Installation](#-getting-started--installation)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Download Pre-trained Model Checkpoints](#2-download-pre-trained-model-checkpoints)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Verify Setup](#4-verify-setup)
  - [5. Run Backend & Frontend](#5-run-backend--frontend)
- [API Endpoints](#-api-endpoints)
- [License](#-license)

---

## ✨ Features

- 🧠 **5 Fine-Tuned NLP Tools**: Locally hosted, high-speed inference without external API latency for core NLP tasks.
- 💬 **Hybrid LLM Stream**: Dual-engine architecture where local models produce structured predictions and the LLM delivers real-time analytical commentary via Server-Sent Events (SSE).
- 🔒 **Firebase Authentication**: Secure user authentication (Email/Password & Google Sign-In).
- 💾 **Cloud Firestore Persistence**: Persistent conversations, message history, and per-chat tool run records.
- ⚡ **Zero-Copy In-Place Model Loading**: Optimized PyTorch / Safetensors loader avoiding redundant memory or disk allocation.
- 🛡️ **Built-in Rate Limiting & Guardrails**: Server-side per-user and per-chat rate limits.
- 🎨 **Modern Dark UI**: Cyber-aesthetic glassmorphism interface built with React and Vanilla CSS.

---

## 🔬 NLP Models & Datasets

TextSphere uses 5 distinct transformer models fine-tuned specifically for each target task:

| Tool | Base Model | Fine-Tuned Dataset | Task Description | Output Format |
| :--- | :--- | :--- | :--- | :--- |
| **Sentiment Analysis** | `distilbert-base-uncased` | [SST-2 (Stanford Sentiment Treebank)](https://huggingface.co/datasets/sst2) | Binary polarity detection (Positive / Negative) | `{ "label": "Positive", "confidence": 0.998 }` |
| **Topic Classification** | `distilbert-base-uncased` | [AG News](https://huggingface.co/datasets/ag_news) | 4-class news classification (World, Sports, Business, Sci/Tech) | `{ "label": "Sci/Tech", "confidence": 0.985 }` |
| **Named Entity Recognition (NER)** | `bert-base-cased` | [CoNLL-2003](https://huggingface.co/datasets/conll2003) | Entity extraction (`PER`, `ORG`, `LOC`, `MISC`) | `[{ "text": "Bill Gates", "label": "PER" }]` |
| **Summarization** | `t5-small` | [CNN / DailyMail](https://huggingface.co/datasets/cnn_dailymail) | Abstractive long-form text summarization | `{ "summary": "Concise overview..." }` |
| **Question Answering (QA)** | `distilbert-base-cased` | [SQuAD v1.1](https://huggingface.co/datasets/squad) | Extractive question answering over reference context | `{ "answer": "Microsoft", "confidence": 0.997 }` |

---

## 📦 How to Get the Models

Because HuggingFace transformer weights total **~1.4 GB**, they are stored on **Google Drive** rather than inside Git.

### Option A: Automatic Download Script (Recommended)

TextSphere includes an automated download utility powered by `gdown`:

```bash
# 1. Install gdown
pip install gdown

# 2. Run the downloader (downloads all 5 models into backend/app/finetuned_models/)
python download_models.py
```

To download only a single model:
```bash
python download_models.py --model sentiment
# choices: sentiment, topic, ner, summarization, qa
```

### Option B: Manual Download from Google Drive

You can also download each folder directly from Google Drive and place the contents inside `backend/app/finetuned_models/<model_name>/`:

| Tool | Google Drive Download Link | Target Local Path |
|---|---|---|
| **Sentiment Analyzer** | [Download Sentiment Model](https://drive.google.com/drive/folders/10R9YmDnIKz9XgCiCUqXszl7l4JS_6Y47?usp=sharing) | `backend/app/finetuned_models/sentiment/` |
| **Topic Classifier** | [Download Topic Model](https://drive.google.com/drive/folders/15lz2jiavSmRKvzZF5j_wyaTFYdne5cjZ?usp=sharing) | `backend/app/finetuned_models/topic/` |
| **Named Entity Recognizer** | [Download NER Model](https://drive.google.com/drive/folders/1RZVF5SEdh6p3wtch9Ep9dzCgh5Det2KA?usp=sharing) | `backend/app/finetuned_models/ner/` |
| **Summarizer** | [Download Summarization Model](https://drive.google.com/drive/folders/1F8wuov-ro9yx-5p7qZvh7OLky-xSZzjP?usp=sharing) | `backend/app/finetuned_models/summarization/` |
| **Question Answering** | [Download QA Model](https://drive.google.com/drive/folders/15nZvciSd6tNZ4QoVJFkw34M4C62CbSIV?usp=sharing) | `backend/app/finetuned_models/qa/` |

---

## 🛠️ Fine-Tuning Models on Your Own

If you want to re-train the models from scratch or train on your own custom datasets, all training pipelines are provided as self-contained Jupyter notebooks in [`finetune_notebooks/`](./finetune_notebooks/):

```
finetune_notebooks/
├── sentiment_finetune.ipynb        # DistilBERT on SST-2
├── topic_finetune.ipynb            # DistilBERT on AG News
├── ner_finetune.ipynb              # BERT on CoNLL-2003
├── summarization_finetune.ipynb    # T5-small on CNN/DailyMail
└── qa_finetune.ipynb               # DistilBERT on SQuAD
```

### Steps to Train on Google Colab (Free GPU):

1. **Open Google Colab** ([colab.research.google.com](https://colab.research.google.com/))
2. Upload the notebook of your choice from `finetune_notebooks/`.
3. Set the hardware accelerator: **Runtime → Change runtime type → T4 GPU**.
4. Run all cells:
   - Loads base model from Hugging Face Hub
   - Tokenizes and preprocesses the dataset
   - Runs `Trainer` / `Seq2SeqTrainer` with learning rate scheduling, evaluation, and checkpoint saving
5. Download the final exported directory (contains `model.safetensors`, `config.json`, `tokenizer.json`, etc.).
6. Place the files into `backend/app/finetuned_models/<model_name>/` to immediately run your new custom weights in TextSphere!

---

## 🏛️ System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                     Frontend (React 18 + Vite)                        │
│   • Tool Selector UI   • SSE Stream Consumer   • Firebase Client Auth │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │ HTTP / SSE Stream
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI Server)                        │
│                                                                       │
│  ┌──────────────────────┐  POST /chat   ┌──────────────────────────┐  │
│  │   Firebase Auth &    │──────────────►│  Tool Pipeline Selector  │  │
│  │   Rate Limit Check   │               └─────────────┬────────────┘  │
│  └──────────────────────┘                             │               │
│                                                       ▼               │
│                            ┌──────────────────────────────────────┐   │
│                            │    Locally Hosted Fine-Tuned Models   │   │
│                            │  (DistilBERT / BERT / T5 on PyTorch) │   │
│                            └──────────────────┬───────────────────┘   │
│                                               │ Prediction output     │
│                                               ▼                       │
│                            ┌──────────────────────────────────────┐   │
│                            │     OpenRouter LLM Commentary        │   │
│                            │     (DeepSeek / Mistral / LLaMA)     │   │
│                            └──────────────────┬───────────────────┘   │
│                                               │ SSE stream chunks     │
│                                               ▼                       │
│                            ┌──────────────────────────────────────┐   │
│                            │    Firestore Message Persistence     │   │
│                            └──────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Tech Stack

- **Frontend**: React 18, Vite, Lucide Icons, Vanilla CSS
- **Backend API**: FastAPI, Uvicorn, Pydantic v2, Python 3.10+
- **Machine Learning**: PyTorch, HuggingFace Transformers, Datasets, Safetensors
- **Auth & Database**: Firebase Authentication, Google Cloud Firestore, `firebase-admin`
- **LLM Integration**: OpenRouter API (`httpx` asynchronous streaming client)

---

## 📁 Project Directory Structure

```
TextSphere/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py              # GET /tools, GET /health, POST /chat
│   │   ├── finetuned_models/          # Model weights (Excluded from git)
│   │   │   ├── ner/                   # BERT weights
│   │   │   ├── qa/                    # DistilBERT QA weights
│   │   │   ├── sentiment/             # DistilBERT SST-2 weights
│   │   │   ├── summarization/         # T5-small weights
│   │   │   └── topic/                 # DistilBERT AG-News weights
│   │   ├── firebase/
│   │   │   ├── auth.py                # Token verification
│   │   │   └── firestore_client.py    # Async Firestore operations
│   │   ├── llm/
│   │   │   └── openrouter_client.py   # Streaming LLM commentary
│   │   ├── tools/
│   │   │   ├── _loader.py             # In-place model loader
│   │   │   ├── ner.py                 # Named Entity Recognizer
│   │   │   ├── qa.py                  # Question Answering
│   │   │   ├── registry.py            # Tool protocol & registry
│   │   │   ├── sentiment.py           # Sentiment Analyzer
│   │   │   ├── summarization.py       # Summarizer
│   │   │   └── topic.py               # Topic Classifier
│   │   ├── config.py                  # Environment settings
│   │   ├── main.py                    # FastAPI entrypoint
│   │   ├── rate_limit.py              # Rate limiting logic
│   │   └── schemas.py                 # Pydantic models
│   ├── .env.example                   # Sample backend environment
│   └── requirements.txt               # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/                # ChatWindow, Sidebar, ToolSelector, etc.
│   │   ├── hooks/                     # useAuth, useChats, useStreamingChat
│   │   ├── pages/                     # Login & Chat Pages
│   │   ├── firebase.js                # Frontend Firebase initialization
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env.example                   # Sample frontend environment
│   └── package.json
├── finetune_notebooks/                # Jupyter / Colab training notebooks
│   └── README.md
├── download_models.py                 # Automatic Google Drive model downloader
├── setup_check.py                     # Environment diagnostics script
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started & Installation

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **Firebase Project** with Authentication (Email/Password & Google) and Firestore Database enabled.
- **OpenRouter API Key** (from [openrouter.ai/keys](https://openrouter.ai/keys))

---

### 1. Clone Repository

```bash
git clone https://github.com/AbdullahRandhawa/TextSphere.git
cd TextSphere
```

---

### 2. Download Pre-trained Model Checkpoints

Download the 5 fine-tuned models directly from Google Drive:

```bash
pip install gdown
python download_models.py
```

---

### 3. Configure Environment Variables

#### Backend Configuration

1. Copy the example environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Open `backend/.env` and provide your credentials:
   ```env
   FIREBASE_CREDENTIALS_PATH=./firebase_credentials.json
   OPENROUTER_API_KEY=sk-or-v1-your-real-openrouter-key
   OPENROUTER_MODEL=deepseek/deepseek-chat
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```
3. Place your Firebase Admin SDK service account key file at `backend/firebase_credentials.json` (download from *Firebase Console → Project Settings → Service accounts → Generate new private key*).

#### Frontend Configuration

1. Copy the example environment file:
   ```bash
   cp frontend/.env.example frontend/.env
   ```
2. Open `frontend/.env` and fill in your Firebase Web App credentials (from *Firebase Console → Project Settings → General → Your apps*):
   ```env
   VITE_FIREBASE_API_KEY=AIzaSy...
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
   VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
   VITE_BACKEND_URL=http://localhost:8000
   ```

---

### 4. Verify Setup

Run the diagnostic script from the project root:

```bash
python setup_check.py
```

When all items display `[OK]`, you are ready to launch!

---

### 5. Run Backend & Frontend

#### Terminal 1 — Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 — Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

Open your browser at **http://localhost:5173** to use TextSphere!

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Healthcheck confirming all 5 local models are loaded | No |
| `GET` | `/tools` | Returns JSON schema descriptors for all registered NLP tools | No |
| `POST` | `/chat` | SSE stream executing selected tool + generating LLM commentary | **Yes** (Bearer Token) |

---

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it for academic or personal projects.