# Hotel Chatbot Backend

This repository contains the backend code for the Hotel Chatbot agent.

## Contents

- `hotel_agent.py` — main logic (unchanged).
- `app.py` — a small Flask wrapper that exposes HTTP endpoints for `availability`, `price`, and `chat`.
- `requirements.txt` — Python dependencies.
- `Procfile` — Gunicorn start command for deploy platforms (Render/Heroku).
- `.env.example` — example environment variables (DO NOT commit actual secrets).

## Environment variables (required)

Set the following environment variables in your hosting platform (Render / Heroku / Railway / etc.):

- `OPENAI_API_KEY` — your OpenAI API key (e.g. `sk-...`)
- `HOTEL_API_BEARER_TOKEN` — bearer token used by `hotel_agent.py` to call the hotel API

## Endpoints

- `GET /health` — health check
- `GET|POST /availability` — calls `get_hotel_availability`. Required params (query or JSON): `json_key`, `start`, `end`, `adults`, `kids`, `minors`.
- `GET|POST /price` — calls `get_hotel_price`. Same params as above.
- `POST /chat` — proxy for conversational calls: send `{ "messages": [...] }`. The wrapper calls `hotel_agent.call_gpt` and returns a compact result.

## Notes

- **Do not** commit secrets to the repository. Use environment variables.
- The `app.py` wrapper is intentionally minimal and does not change the logic inside `hotel_agent.py`. It simply exposes endpoints so you can deploy the code as a web service.
