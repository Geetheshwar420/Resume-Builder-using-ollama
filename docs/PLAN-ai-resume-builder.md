# Implementation Plan - AI Resume Builder (Three-Tier System)

This project implements a three-tier AI Resume Builder system with a FastAPI backend (the AI Engine) and two Streamlit frontends (Admin Portal and Client Site). The system uses Ollama (Llama 3.2 1B) for resume generation and includes security, guardrails, and quality evaluation.

## User Review Required

> [!IMPORTANT]
> **Tunneling Requirement**: Since the AI Engine (FastAPI) will run locally via tunneling (e.g., Ngrok), the Client Site and Admin Portal will need the *public* URL of the tunnel to communicate if they are deployed in the cloud.
> 
> **Ollama Setup**: You must have [Ollama](https://ollama.com/) installed and the `llama3.2:1b` model pulled locally (`ollama pull llama3.2:1b`) for the backend to function.

## Proposed Changes

### 1. Project Structure
We will organize the project into three distinct directories to support clean Dockerization and independent deployments.

- `engine/`: FastAPI backend service.
- `admin/`: Streamlit administration dashboard.
- `client/`: Streamlit user-facing website.
- `shared/`: Shared Docker configuration and documentation.

---

### 2. The AI Engine (`engine/`)

#### [NEW] [engine.py](file:///c:/Users/geeth/OneDrive/Videos/Resume Builder/engine/engine.py)
- **FastAPI Application**: Core service handling resume generation.
- **Security Middleware**: Validates `X-API-KEY` against `keys.json`.
- **Rate Limiting**: Uses `slowapi` or similar to prevent resource exhaustion.
- **Ollama Integration**: Calls Llama 3.2 1B for two modes:
    1. **Resume Generation**: Raw data to professional bullet points.
    2. **LLM-as-a-Judge**: Evaluates the generated content (Score 1-10).
- **Guardrails**:
    - Input: Basic prompt injection detection.
    - Output: Hallucination/Consistency checks.
- **Endpoints**:
    - `POST /generate`: Returns JSON with resume text and quality score.

#### [NEW] [keys.json](file:///c:/Users/geeth/OneDrive/Videos/Resume Builder/engine/keys.json)
- Initialized as an empty dictionary `{}` to store valid API keys.

---

### 3. The Key Manager (`admin/`)

#### [NEW] [admin_portal.py](file:///c:/Users/geeth/OneDrive/Videos/Resume Builder/admin/admin_portal.py)
- **Streamlit App**: Admin-only interface.
- **Functionality**:
    - Button to generate random UUID-based keys.
    - Logic to update `../engine/keys.json`.
    - Table displaying all active keys.

---

### 4. The Resume Website (`client/`)

#### [NEW] [client_site.py](file:///c:/Users/geeth/OneDrive/Videos/Resume Builder/client/client_site.py)
- **Streamlit App**: User-facing interface.
- **Form**: Fields for Experience, Skills, Education, and Contact info.
- **Security**: Loads `AI_ENGINE_KEY` from `.env`.
- **Outputs**:
    - Renders resume in a premium UI.
    - **Downloadable PDF**: Uses `fpdf2` for clean professional formatting.
    - **Downloadable TXT**: Plain text version.

---

### 5. Deployment & Configuration

#### [NEW] [docker-compose.yml](file:///c:/Users/geeth/OneDrive/Videos/Resume Builder/docker-compose.yml)
- Configures three services: `ai-engine`, `admin-portal`, and `client-site`.
- Note: `ai-engine` will need `network_mode: host` or specific config to talk to a local Ollama instance on the host machine.

#### [NEW] [.env.example](file:///c:/Users/geeth/OneDrive/Videos/Resume Builder/.env.example)
- Fields for `AI_ENGINE_URL` and `AI_ENGINE_KEY`.

---

## Open Questions

- **PDF Styling**: Do you have a specific resume template style (Modern, Classic, Creative) in mind for the PDF output?
- **Auth for Admin**: Should the `admin_portal.py` have a simple password login to prevent unauthorized key generation in the cloud?

## Verification Plan

### Automated Tests
- `pytest` for `engine.py` to verify API key validation and response structures.
- Mocking Ollama calls to ensure the logic works without the LLM during CI.

### Manual Verification
- Start local Ollama, run `engine.py`.
- Generate a key via `admin_portal.py`.
- Use the key in `client_site.py` to generate and download a resume.
- Verify Docker build: `docker-compose up --build`.
