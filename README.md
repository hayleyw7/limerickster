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

Easily create a personalized limerick from a few details.

Turn a person’s profile into a custom **five-line limerick** (AABBA rhyme, playful and personal).

**Live app:** https://hayleyw7-limerickster.hf.space/

## Form fields

| Field | Required? | Purpose |
|-------|-----------|---------|
| **Name** | Yes | Who the limerick is about |
| **Location** | Yes | City or region (great for rhymes) |
| **Pronouns** | Yes | She/her, he/him, or they/them (strictly enforced in the poem) |
| **Hobbies 1–3** | Yes | All three hobbies are required |
| **Pets** | No | Pets and animal companions |
| **Favorite food or drink** | No | Sensory detail |
| **Appearance** | No | Look and style detail for the poem |
| **Job** | No | Day job or dream job |
| **Other notes** | No | Anything else to include (such as partner named Glorbo, inside joke about pizza, or to avoid a topic entirely) |
| **Tone** | No (defaults to cheerful) | cheerful, wholesome, sarcastic, dramatic, absurd, or romantic |

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # add your free GROQ_API_KEY (see below)
python app.py
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080).

On macOS, **avoid port 5000** — AirPlay Receiver often uses it and returns HTTP 403 (“Access denied”) instead of your app.

## AI (Groq — free tier)

Limerickster uses [Groq](https://console.groq.com) for fast, free-tier inference (no ChatGPT Pro or OpenAI billing required).

1. Sign in at [console.groq.com](https://console.groq.com)
2. Create an API key at [console.groq.com/keys](https://console.groq.com/keys)
3. Add to `.env`:
   ```bash
   GROQ_API_KEY=gsk_...
   ```
4. Restart `python app.py`

Optional: change the model with `GROQ_MODEL` (default `llama-3.3-70b-versatile`).

## Link previews (Discord, Twitter, Facebook)

The app ships with a favicon, Apple touch icon, and a 1200×630 Open Graph image in `static/`, using the same palette as `style.css` (cream, lavender, peach, ink, mint, coral). Meta tags are set in `templates/index.html`.

To regenerate PNG/JPEG assets after palette changes:

```bash
pip install pillow
python scripts/generate_brand_assets.py
```

For social crawlers to fetch the preview image, set **`SITE_URL`** in `.env` to your public HTTPS origin (e.g. `https://hayleyw7-limerickster.hf.space`). Without it, local `127.0.0.1` URLs won’t work when you paste the link elsewhere.

After deploying, you can refresh cached previews with each platform’s debugger (e.g. [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/), [Twitter Card Validator](https://cards-dev.twitter.com/validator)).

## What you get

The page displays one **limerick** — five lines, AABBA rhyme, tuned to the profile and tone you chose.

## Rate limiting

Per-IP limits protect the generate endpoint from abuse (defaults: **10 generate requests/minute**, **120 requests/hour** overall). Tune in `.env`:

```bash
RATE_LIMIT_GENERATE=10 per minute
RATE_LIMIT_DEFAULT=120 per hour
```

Behind a reverse proxy, configure your proxy to set `X-Forwarded-For` so limits apply to real client IPs. Local requests from `127.0.0.1` are exempt by default (`RATE_LIMIT_LOCAL_EXEMPT=true`).

## Requirements

- Python 3.10+
- A free [Groq API key](https://console.groq.com/keys)

## License

Licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) (GPL-3.0).
