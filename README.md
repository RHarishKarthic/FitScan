# 🚀 FitScan — AI Resume Scanner & HR Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_AI-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai/)

A comprehensive, full-stack AI recruitment platform designed to intelligently parse, rank, and evaluate candidate resumes against Job Descriptions using Natural Language Processing (NLP) and local offline Generative AI.

---

## 🌟 Key Features

- 📄 **Automated Resume & JD Parsing**: Instantly extracts contact email, years of experience, core skills, education, projects, and certifications from `.txt`, `.pdf`, and `.docx` files.
- ⚡ **Dual Matching Engine**:
  - *Heuristic NLP*: Uses **SpaCy** (`en_core_web_sm`) to cross-reference extracted candidate skills and experience against JD requirements.
  - *Semantic AI*: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) for deep-context cosine similarity embedding math.
- 🤖 **Local Offline Generative Insights**: Integrated with **Ollama** (`llama3` / `resume_scanner`) to natively generate specific strengths, missing skill gaps, and personalized candidate interview questions completely offline with auto-discovery and intelligent fallback handling.
- 📊 **Rich Dashboard Interface**: Responsive React + Tailwind CSS dashboard (`frontend v2`) featuring metric tracking, shortlist management, candidate details views, and interactive drag-and-drop file uploaders.
- 📁 **Data Persistence & Reporting**: Persistent disk storage (`uploads/state.json`) and instant exports for shortlist reports in **PDF** (ReportLab) and **Excel** (`openpyxl` / `pandas`).
- 🐳 **Fully Containerized**: 1-click Docker Compose setup for backend microservices and frontend web server.

---

## 🏗️ Architecture Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Recharts, Lucide React, Axios.
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, ReportLab, OpenPyXL, Pandas.
- **AI & NLP Processing**: 
  - `SpaCy` (`en_core_web_sm`) for entity recognition and vocabulary matching.
  - `SentenceTransformers` (`all-MiniLM-L6-v2`) for semantic text vector embeddings.
  - `Scikit-learn` for cosine similarity vector math.
  - `Ollama` for local Large Language Model inferencing (`llama3` / custom HR persona).

---

## 📁 Project Structure

```text
FitScan/
├── backend/
│   ├── app.py                 # FastAPI endpoints & persistent state handling
│   ├── resume_parser.py       # Resume parsing engine & contact/name extraction
│   ├── jd_parser.py           # Job description requirement parser
│   ├── matcher.py             # Dual heuristic + vector cosine similarity engine
│   ├── llm_generator.py       # Ollama LLM interface & heuristic fallback builder
│   ├── anonymizer.py          # PII masking utility
│   ├── create_labels.py       # Ground-truth dataset label generator
│   ├── Modelfile              # Ollama system prompt instructions for HR persona
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container configuration
├── frontend v2/               # React 18 + Vite + Tailwind dashboard application
│   ├── src/
│   │   ├── components/        # UI components & dashboard layout
│   │   ├── pages/             # Dashboard, Candidates, Upload, Reports, Metrics
│   │   ├── services/          # Axios API communication layer
│   │   └── types/             # TypeScript type definitions
│   ├── vite.config.ts         # Vite server configuration
│   ├── package.json           # Node.js dependencies
│   └── Dockerfile             # Frontend container configuration
├── data/                      # Sample resumes, JDs, and ground truth files
├── docker-compose.yml         # Multi-container container orchestration
└── README.md                  # Project documentation
```

---

## 🚀 Quickstart Guide

### Option A: Running with Docker (Recommended)

#### 1. Prerequisites
- [Docker & Docker Desktop](https://www.docker.com/) installed and running.
- [Ollama](https://ollama.ai/) installed on your host machine with `llama3` pulled:
  ```bash
  ollama run llama3
  ```

#### 2. Setup the HR AI Persona Model
Initialize the custom HR model using the provided [Modelfile](file:///c:/Users/haris/Downloads/FitScan/FitScan/backend/Modelfile):
```bash
ollama create resume_scanner -f backend/Modelfile
```

#### 3. Spin up the Platform
From the project root directory, run:
```bash
docker-compose up --build
```

#### 4. Access the Platform
- **Frontend Dashboard**: `http://localhost:5175`
- **Backend API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

### Option B: Running Locally (Development Mode)

#### 1. Start Backend API
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Start Frontend App
In a new terminal window:
```bash
cd "frontend v2"
npm install
npm run dev
```
Navigate to `http://localhost:5175` in your web browser.

---

## 🔌 API Reference Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/dashboard/stats` | Fetches overall recruitment metrics & score averages |
| `POST` | `/api/upload_jd` | Uploads a Job Description file (`.pdf`, `.docx`, `.txt`) |
| `POST` | `/api/upload_jd_text` | Parses pasted Job Description text |
| `POST` | `/api/upload_resumes` | Processes batch candidate resume uploads against active JD |
| `GET` | `/api/candidates` | Retrieves candidate ranking list with filter options |
| `GET` | `/api/candidates/{id}` | Fetches candidate details (strengths, skill gaps, interview questions) |
| `POST` | `/api/candidates/{id}/shortlist` | Adds candidate to recruitment shortlist |
| `GET` | `/api/export` | Downloads recruitment report (`format=pdf` or `format=excel`) |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
