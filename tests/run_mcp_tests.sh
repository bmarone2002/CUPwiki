#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${ROOT}/.venv-mcp/bin/python"
UV="${ROOT}/tools/uv-bin/uv"

if [[ ! -x "$PY" ]]; then
  echo "MCP venv mancante. Bootstrap:"
  echo "  ${UV} python install 3.12"
  echo "  ${UV} venv --python 3.12 ${ROOT}/.venv-mcp"
  echo "  ${UV} pip install --python ${PY} -r ${ROOT}/mcp-server/requirements.txt"
  exit 1
fi

echo "== smoke test =="
"$PY" "${ROOT}/tests/smoke_mcp_read.py"
echo
echo "== operational read demo =="
"$PY" "${ROOT}/tests/mcp_operational_read_demo.py"
