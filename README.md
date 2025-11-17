💼 AI Job Recommendation System

An intelligent job recommendation engine powered by FAISS, Semantic Embeddings, FastAPI, and Streamlit.
It matches users to jobs based on profile similarity, job titles, skills, and location — with a fast FAISS backend and incremental embedding updates.

🚀 Features
🔍 AI-Powered Matching

Semantic job title matching

Strong autocorrect for user titles (e.g. “data scienctist” → “data scientist”)

Fuzzy skill matching

Location-based scoring

Weighted final score using FAISS similarity

⚡ High-Speed Semantic Search

Uses intfloat/e5-large-v2 embeddings

FAISS index for millisecond search

Ranks thousands of jobs in <100ms

🔄 Incremental Embedding Updater

Detects new database rows

Generates embeddings only for new jobs

Appends them into:

jobs_embeddings.npy

job_title_embs.npy

job_ids.npy

job_metadatas.npy

faiss_index.bin

🌐 Streamlit Web App

Beautiful UI for end-users

Match score + job details

Simple user ID input → instant results

🖥️ FastAPI Backend

REST endpoint:

GET /recommend/{user_id}?top_k=10


Clean JSON output

Hot reload endpoint for incremental updates

📁 Project Structure
job_recommender/
│
├── src/
│   ├── api.py              → FastAPI backend
│   ├── app.py              → Streamlit app
│   ├── pipeline.py         → Full embedding builder + recommender
│   ├── incremental.py      → Incremental embedding updater
│   ├── database.py         → MySQL connectors
│   ├── faiss_index.py      → FAISS build/load
│   ├── embedding_local.py  → Semantic embedding generation
│
├── data/
│   ├── jobs_cleaned.csv     (ignored)
│   └── embeddings/          (ignored — FAISS + .npy files)
│
├── .gitignore
├── requirements.txt
└── README.md

🛠️ Installation
1️⃣ Clone repo
git clone https://github.com/vivekvisko11/job_recommender.git
cd job_recommender

2️⃣ Create environment
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

🔧 Setup
1️⃣ Prepare your MySQL tables

jobs table

users table
Or modify script to load CSV.

2️⃣ Build embeddings (first time only)
python -m src.pipeline


This will generate:

jobs_embeddings.npy

job_ids.npy

job_title_embs.npy

job_metadatas.npy

faiss_index.bin

Stored in:

data/embeddings/

🔁 Incremental Updates
Run incremental updater:
python -m src.incremental

One-time update:
python -m src.incremental --once

🌐 Run API
uvicorn src.api:app --reload --port 8000


Example:

GET http://127.0.0.1:8000/recommend/1246?top_k=10

🖥️ Run Streamlit App
streamlit run src/app.py

📦 Git Notes

These are NOT uploaded to GitHub:

✔ venv/
✔ data/embeddings/
✔ .bin FAISS index
✔ .csv raw job data
✔ any file >100MB
