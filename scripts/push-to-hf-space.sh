#!/usr/bin/env bash
# Push main to Hugging Face Space (hayleyw7/limerickster).
# Usage:
#   HF_TOKEN=hf_xxxx ./scripts/push-to-hf-space.sh
# Get a write token: https://huggingface.co/settings/tokens

set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "Missing HF_TOKEN."
  echo "Create a write token: https://huggingface.co/settings/tokens"
  echo "Then run: HF_TOKEN=hf_xxx ./scripts/push-to-hf-space.sh"
  exit 1
fi

REMOTE="https://hayleyw7:${HF_TOKEN}@huggingface.co/spaces/hayleyw7/limerickster"
git push "${REMOTE}" main
echo "Pushed. Live app: https://hayleyw7-limerickster.hf.space/"
echo "Space admin: https://huggingface.co/spaces/hayleyw7/limerickster"
