import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import APIStatusError, OpenAI, RateLimitError

load_dotenv(Path(__file__).resolve().parent / ".env")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Limerickster, a witty poet-engineer who turns personal profiles into
limerick-themed project kits. You write in clear, playful English.

A limerick has 5 lines: AABBA rhyme scheme, lines 1/2/5 rhyme, lines 3/4 rhyme,
anapestic meter (da-da-DUM), and light humor.

PRONOUN COMPLIANCE (mandatory — never violate):
The user specifies exactly one pronoun set for the subject. Use ONLY that set in the limerick
for every reference to the person (subject, object, possessive, reflexive). Never mix sets.

- she/her ONLY: she, her, hers, herself. Never he/him/his/himself or they/them/their/theirs/themselves.
- he/him ONLY: he, him, his, himself. Never she/her/hers/herself or they/them/their/theirs/themselves.
- they/them ONLY (singular): they, them, their, theirs, themselves. Never he/him or she/her forms.

Using the wrong pronouns is a critical failure. You may use their name sometimes, but any pronoun
must match the required set.

PROPER NOUN AND BRAND CAPITALIZATION:
Capitalize people's names, place names, and brand/product/app names with normal English spelling.
Examples: "alex" → "Alex"; "new york" → "New York"; "DISCORD" → "Discord"; "spotify" → "Spotify".
If the user types a brand or name in ALL CAPS, treat it as casual typing (not emphasis) and use
standard form: DISCORD → Discord, ROBLOX → Roblox, NYC → New York City.
Do NOT capitalize common nouns or generic activities: memes, gaming, cats, pizza, hiking stay
lowercase unless part of a proper name (e.g. "World of Warcraft").

WORD BAN (mandatory):
Never use the word "fine" in the limerick — not as an adjective, adverb, or in any phrase (e.g. "just fine", "feeling fine").

Return ONLY valid JSON with this exact structure:
{
  "limerick": "five-line limerick with \\n between lines",
  "readme": "full README.md markdown as a string",
  "rhyme_bank": {"word": ["rhyme1", "rhyme2", ...], ...},
  "writing_tips": ["tip1", "tip2", "tip3"],
  "repo_name": "kebab-case-suggested-repo-name",
  "tagline": "one short punchy tagline"
}

Thank you for following every rule above with care."""


PRONOUN_RULES = {
    "she/her": (
        "REQUIRED PRONOUNS: she/her only (she, her, hers, herself). "
        "Forbidden for this person: he, him, his, himself, they, them, their, theirs, themselves."
    ),
    "he/him": (
        "REQUIRED PRONOUNS: he/him only (he, him, his, himself). "
        "Forbidden for this person: she, her, hers, herself, they, them, their, theirs, themselves."
    ),
    "they/them": (
        "REQUIRED PRONOUNS: they/them only — singular they (they, them, their, theirs, themselves). "
        "Forbidden for this person: he, him, his, himself, she, her, hers, herself."
    ),
}


def build_user_prompt(profile: dict) -> str:
    lines = ["Please create a complete limerick creation kit for this person:\n"]

    labels = {
        "name": "Name",
        "location": "Location",
        "pronouns": "Pronouns",
        "hobby_1": "Hobby 1",
        "hobby_2": "Hobby 2",
        "hobby_3": "Hobby 3",
        "job": "Job",
        "pets": "Pets",
        "favorite_food": "Favorite food or drink",
        "physical_trait": "Appearance",
        "tone": "Desired tone",
    }
    notes = profile.get("other_notes", "").strip()
    for key, label in labels.items():
        value = profile.get(key, "").strip()
        if value:
            lines.append(f"- {label}: {value}")
    if notes:
        lines.append(f"- Other notes: {notes}")
        lines.append(
            "\n=== OTHER NOTES (follow closely) ===\n"
            "Honor requests in Other notes 100%, no matter what. If the user asks for something "
            "to be included or excluded, treat that as mandatory in the limerick."
        )

    name = profile.get("name", "").strip()
    pronouns = profile.get("pronouns", "").strip()
    rules = PRONOUN_RULES.get(pronouns)
    if rules:
        lines.append(f"\n=== PRONOUN REQUIREMENT (check every line of the limerick) ===")
        lines.append(rules)
        if name:
            lines.append(
                f"Subject's name is {name}. Use {pronouns} pronouns whenever you refer to "
                f"{name} with a pronoun — never another set."
            )
        lines.append(
            "Before returning JSON, re-read the limerick and confirm zero wrong pronouns."
        )

    lines.append(
        "\nWeave in as many provided details as fit naturally. "
        "The limerick is the star — make it personal, funny, and true to the tone. "
        "Never use the word \"fine\" in the limerick. "
        "Normalize ALL CAPS brands and names (DISCORD → Discord). "
        "Capitalize proper nouns only — not common words like hobbies or memes."
    )
    lines.append("\nThank you!")
    return "\n".join(lines)


def _friendly_api_error(exc: Exception) -> str:
    code = None
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error") or {}
        code = err.get("code") or err.get("type")

    text = str(exc)
    status = getattr(exc, "status_code", None)

    if status == 401:
        return (
            "Invalid Groq API key. Get a free key at https://console.groq.com "
            "and set GROQ_API_KEY in your .env file."
        )
    if status == 429:
        return "Groq rate limit reached. Wait a moment and try again."

    return f"AI request failed: {text}"


def generate_kit(profile: dict) -> dict:
    api_key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com "
            "and add it to your .env file."
        )

    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    model = os.environ.get("GROQ_MODEL", DEFAULT_MODEL)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(profile)},
            ],
            response_format={"type": "json_object"},
            temperature=0.75,
        )
    except (APIStatusError, RateLimitError) as e:
        raise ValueError(_friendly_api_error(e)) from e

    raw = response.choices[0].message.content
    return json.loads(raw)
