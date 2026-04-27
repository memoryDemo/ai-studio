#!/usr/bin/env bash
set -euo pipefail

CHATBOT_HOST="${CHATBOT_HOST:-127.0.0.1}"
CHATBOT_PORT="${CHATBOT_PORT:-8080}"
STUDIO_HOST="${STUDIO_HOST:-127.0.0.1}"
STUDIO_PORT="${STUDIO_PORT:-7860}"
MEYO_CONFIG="${MEYO_CONFIG:-/opt/meyo/configs/meyo.toml}"

export HOST="${CHATBOT_HOST}"
export PORT="${CHATBOT_PORT}"
export FRONTEND_BUILD_DIR="${FRONTEND_BUILD_DIR:-/opt/meyo-chatbot/build}"
export STATIC_DIR="${STATIC_DIR:-/opt/meyo-chatbot/backend/open_webui/static}"
export WEBUI_SECRET_KEY="${WEBUI_SECRET_KEY:-}"

mkdir -p \
  /data/meyo-chatbot \
  /data/meyo-studio-flow \
  /data/meyo-studio-flow/knowledge_bases \
  /opt/meyo/logs \
  /opt/meyo/pilot

if [[ -z "${WEBUI_SECRET_KEY:-}" && -z "${WEBUI_JWT_SECRET_KEY:-}" ]]; then
  key_file="${WEBUI_SECRET_KEY_FILE:-/data/meyo-chatbot/.webui_secret_key}"
  if [[ ! -f "${key_file}" ]]; then
    head -c 32 /dev/urandom | base64 > "${key_file}"
  fi
  export WEBUI_SECRET_KEY
  WEBUI_SECRET_KEY="$(cat "${key_file}")"
fi

pids=()

terminate() {
  if ((${#pids[@]})); then
    kill "${pids[@]}" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
}
trap terminate EXIT INT TERM

cd /opt/meyo
MEYO_LOG_LEVEL="${MEYO_LOG_LEVEL:-info}" \
  /opt/meyo/.venv/bin/meyo --log-level "${MEYO_LOG_LEVEL:-info}" start webserver --config "${MEYO_CONFIG}" &
pids+=("$!")

cd /opt/meyo-chatbot/backend
/opt/venvs/meyo-chatbot/bin/python -m uvicorn open_webui.main:app \
  --host "${CHATBOT_HOST}" \
  --port "${CHATBOT_PORT}" \
  --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-*}" \
  --workers "${CHATBOT_UVICORN_WORKERS:-1}" &
pids+=("$!")

cd /opt/meyo-studio-flow
/opt/meyo-studio-flow/.venv/bin/langflow run \
  --frontend-path /opt/meyo-studio-flow/src/backend/base/langflow/frontend \
  --host "${STUDIO_HOST}" \
  --port "${STUDIO_PORT}" \
  --log-level "${STUDIO_LOG_LEVEL:-info}" \
  --no-open-browser &
pids+=("$!")

nginx -g "daemon off;" &
pids+=("$!")

set +e
wait -n "${pids[@]}"
exit_code=$?
set -e
terminate
exit "${exit_code}"
