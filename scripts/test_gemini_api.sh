#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"

start_server() {
  export DEBUG_MODE="${DEBUG_MODE:-true}"
  echo "Starting dev server on ${HOST}:${PORT} (DEBUG_MODE=${DEBUG_MODE})"
  uvicorn main:app --host "$HOST" --port "$PORT" --reload
}

check_health() {
  curl -sS "http://localhost:${PORT}/"
  echo
}

mock_push() {
  local auth_key="${GIT_ACTIONS_WEBHOOK_SECRET:-}"
  if [[ -z "$auth_key" ]]; then
    echo "GIT_ACTIONS_WEBHOOK_SECRET is missing. Add it to .env first."
    exit 1
  fi

  curl -sS -X POST "http://localhost:${PORT}/api/menu/push/" \
    -H "Content-Type: application/json" \
    -H "x-auth-key: ${auth_key}" \
    --data @- <<'JSON'
{
  "meal": "lunch",
  "html_data": {
    "west": "<html><body><div>05/05(Tue) Lunch Pork Bulgogi (10) Kimchi White Rice Orange Juice</div></body></html>",
    "east": "<html><body><div>05/05(Tue) Lunch Bibimbap (1,2,5) Green Salad Apple</div></body></html>"
  }
}
JSON
  echo
}

test_gemini() {
  python - <<'PY'
import asyncio
from llm_service import process_all_menus_with_gemini

html_data = {
    "west": "<html><body><div>05/05(Tue) Lunch Pork Bulgogi (10) Kimchi White Rice Orange Juice</div></body></html>",
    "east": "<html><body><div>05/05(Tue) Lunch Bibimbap (1,2,5) Green Salad Apple</div></body></html>",
}

async def main():
    out = await process_all_menus_with_gemini("Lunch", html_data, "2026-05-05 (Tue)")
    print("=== GEMINI RESPONSE START ===")
    print(out)
    print("=== GEMINI RESPONSE END ===")

asyncio.run(main())
PY
}

usage() {
  cat <<'EOF'
Usage: ./scripts/dev.sh <command>

Commands:
  start   Start local FastAPI server in debug mode
  health  Hit local health endpoint
  mock    Send a mock push payload to local endpoint
  gemini  Run direct Gemini smoke test
EOF
}

case "${1:-}" in
  start)
    start_server
    ;;
  health)
    check_health
    ;;
  mock)
    mock_push
    ;;
  gemini)
    test_gemini
    ;;
  *)
    usage
    exit 1
    ;;
esac
