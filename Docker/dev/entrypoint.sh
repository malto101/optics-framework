#!/bin/bash
set -euo pipefail

# Default destination for credentials inside the container
CRED_PATH="/secrets/mozark-icici.json"

# Helper: write credentials safely
write_credentials() {
  local content="$1"
  mkdir -p "$(dirname "$CRED_PATH")"
  # use a temp file and mv to avoid partial writes
  local tmpfile
  tmpfile=$(mktemp)
  printf '%s' "$content" > "$tmpfile"
  chmod 600 "$tmpfile"
  mv "$tmpfile" "$CRED_PATH"
}

# If the env var GOOGLE_CREDENTIALS_JSON is provided, write it to the file
if [ -n "${GOOGLE_CREDENTIALS_JSON:-}" ]; then
  write_credentials "$GOOGLE_CREDENTIALS_JSON"
  echo "Wrote credentials to $CRED_PATH"
fi

# If the credentials file exists (either baked-in or written), export the env var
if [ -f "$CRED_PATH" ]; then
  # ensure permissions
  chmod 600 "$CRED_PATH" || true
  export GOOGLE_APPLICATION_CREDENTIALS="$CRED_PATH"
  echo "Exported GOOGLE_APPLICATION_CREDENTIALS=$CRED_PATH"
fi

# Exec the main process
exec "$@"
