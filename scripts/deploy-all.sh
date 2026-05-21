#!/usr/bin/env bash
# Push code + set Space secrets. Needs:
#   .hf_token  — one line, your HF *write* token (gitignored)
#   .env       — GROQ_API_KEY (already there)

set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -f .hf_token ]]; then
  HF_TOKEN="$(tr -d '[:space:]' < .hf_token)"
elif [[ -n "${HF_TOKEN:-}" ]]; then
  :
else
  echo "Create .hf_token in the project root with your HF write token (one line)."
  echo "https://huggingface.co/settings/tokens"
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "Missing .env with GROQ_API_KEY"
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

if [[ -z "${GROQ_API_KEY:-}" ]]; then
  echo "GROQ_API_KEY not set in .env"
  exit 1
fi

export HF_TOKEN

echo "→ Pushing to Hugging Face Space…"
git push "https://hayleyw7:${HF_TOKEN}@huggingface.co/spaces/hayleyw7/limerickster" main

echo "→ Setting Space secrets…"
python3 -m pip install -q huggingface_hub
python3 <<'PY'
import os
from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
repo = "hayleyw7/limerickster"
api.add_space_secret(repo_id=repo, key="GROQ_API_KEY", value=os.environ["GROQ_API_KEY"])
api.add_space_secret(
    repo_id=repo,
    key="SITE_URL",
    value="https://hayleyw7-limerickster.hf.space",
)
print("Secrets updated (Space will restart).")
PY

echo "Live app: https://hayleyw7-limerickster.hf.space/"
echo "Space admin: https://huggingface.co/spaces/hayleyw7/limerickster"
echo "When the App tab shows Running, test Generate Limerick."
echo "For friends: set Space visibility to Public in Settings."
