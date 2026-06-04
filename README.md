---
title: Limerickster
emoji: ⌨️
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
short_description: Easily create a personalized limerick from a few details.
thumbnail: https://hayleyw7-limerickster.hf.space/static/og-image.jpg
---

# Limerickster

Turn a few details about someone into a custom **five-line limerick**—AABBA rhyme, playful and personal.

**Try it:** https://hayleyw7-limerickster.hf.space/

## How to use it

1. Open the app and add a **name**, **location**, and **pronouns** (she/her, he/him, or they/them).
2. Fill in **three hobbies**—they help drive the rhymes.
3. Add anything else you like: pets, favorite food or drink, appearance, job, or other notes (inside jokes, a partner’s name, topics to skip, and so on).
4. Pick a **tone** if you want—cheerful is the default; you can also choose wholesome, sarcastic, dramatic, absurd, or romantic.
5. Generate. You get one limerick back—five lines, matched to what you entered.

## Tech stack

| Layer | What |
| --- | --- |
| **Language** | Python 3.11 (Docker / Hugging Face Space); local dev may use 3.8+ |
| **Web** | [Flask](https://flask.palletsprojects.com/) — server-rendered UI and a JSON API |
| **Production server** | [Gunicorn](https://gunicorn.org/) |
| **Frontend** | Vanilla HTML, CSS, and JavaScript (Jinja templates, no React/Vue) |
| **AI** | [Groq](https://groq.com/) — OpenAI-compatible API; default model **Llama 3.3 70B** (`llama-3.3-70b-versatile`) |
| **AI client** | [OpenAI Python SDK](https://github.com/openai/openai-python) pointed at Groq’s base URL |
| **Rate limiting** | [Flask-Limiter](https://flask-limiter.readthedocs.io/) (in-memory store) |
| **Config** | Environment variables via [python-dotenv](https://github.com/theskumar/python-dotenv) (`.env`) |
| **Hosting** | [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces) — Docker SDK, port 7860 |

Generation is prompt-driven: the model returns structured JSON (limerick plus optional kit fields like rhyme bank and writing tips). Pronoun rules, tone, and a word ban are enforced in the system prompt in `ai.py`.

## Run locally

1. Clone the repo and create a virtualenv (optional but recommended).
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set a free **Groq** API key from [console.groq.com](https://console.groq.com/keys).
4. Start the dev server: `python app.py` (defaults to `http://127.0.0.1:8080`).

Optional env vars: `GROQ_MODEL`, `PORT`, `SITE_URL`, `RATE_LIMIT_GENERATE`, `RATE_LIMIT_DEFAULT`.

## Deploy

The live app runs as a **Docker Space** on Hugging Face. `scripts/deploy-all.sh` pushes code and syncs secrets (HF token + `GROQ_API_KEY`). See `Dockerfile` and `scripts/push-to-hf-space.sh` for the container build.

## License

Licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) (GPL-3.0).
