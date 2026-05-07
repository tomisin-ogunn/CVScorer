# CV Scorer Backend (FastAPI)

This is a simple FastAPI backend for the CV Scorer project. It exposes an API
endpoint that accepts CV and Job Description text and returns a (placeholder)
similarity score.

## Setup

From the `backend` folder (inside `cv-scorer`):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the server

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

### Endpoints

- `GET /health` – simple health check
- `POST /score` – calculate a placeholder similarity score

#### POST /score

Request body (JSON):

```json
{
  "cv_text": "string",
  "job_description": "string"
}
```

Response body (JSON):

```json
{
  "score": 85
}
```

> Note: The scoring is currently random. Replace the logic in
> `main.py` with real similarity computation later.

Author: Tomisin Ogunnusi, Bilal Ahmed  09/02/2026

