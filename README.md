# AI Resume Builder - Three-Tier System

A professional, ATS-friendly resume generation system powered by FastAPI, Streamlit, and Llama 3.2 1B (via Ollama).

## 🏗️ System Architecture

![System Architecture](./System%20architecture.png)

### Three-Tier Ecosystem
1.  **AI Engine (Backend)**: The core brain. Handles security sanitization, XML prompt tagging, 15s hardware timeouts (for Iris GPU protection), and final quality scoring.
2.  **Admin Portal**: Secure gateway for generating and managing API Keys and user registration.
3.  **Client Site**: The front-facing resume portal for end-users to input data and generate PDFs.

## 🚀 Quick Start

### 1. Prerequisites
- [Ollama](https://ollama.com/) installed and running.
- Pull the model: `ollama pull llama3.2:1b`
- Docker & Docker Compose.

### 2. Configuration
- Copy `.env.example` to `.env`.
- Set `AI_ENGINE_URL` (use your tunnel URL if deploying to cloud).

### 3. Run with Docker
```bash
docker-compose up --build
```
The database will be automatically initialized and pre-seeded with the admin account on the first run.

### 4. Workflow
1.  **Login/Register**: Access the Auth Portal at `http://localhost:8501`.
2.  **Generate Key**: Once logged in, generate a unique API key for your client.
3.  **Setup Client**: Add your generated key to your `.env` file under `AI_ENGINE_KEY`.
4.  **Build Resume**: Access the Client Site at `http://localhost:8502` and start generating!

## 🛡️ Stability & Security Layer (Chaos-Resistant)
- **Regex Sanitization**: Strips HTML tags, `<script>` blocks, and non-standard symbols.
- **Payload Validation**: Strict Pydantic models for input length (max 1,500 chars) to prevent OOM errors on local GPUs.
- **Watchdog Timeout**: 15-second hardware timeout for all processing steps to protect system responsiveness.
- **XML Shielding**: Instructs Ollama to prioritize guardrails using specific tagging patterns.

## 📄 API Reference (FastAPI Swagger)
The backend engine provides an interactive documentation interface for developers:
- **Swagger UI**: Access at `http://localhost:8000/docs` to test endpoints and view schemas.
- **Redoc**: Access at `http://localhost:8000/redoc` for a cleaner, documentation-focused layout.

## 📁 Shared Persistence
The system uses a shared Docker volume for the SQLite database (`data/resume_builder.db`), ensuring user and key persistence across service restarts.

## 📄 ATS-Friendly PDF
The system uses the `fpdf2` library to generate clean, text-searchable PDFs that are optimized for Applicant Tracking Systems (ATS).
