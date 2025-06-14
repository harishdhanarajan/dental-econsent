#!/usr/bin/env bash
set -e

# Decode the base64-encoded JSON into a file the app can read
mkdir -p /secrets
echo "$GOOGLE_CREDENTIALS_B64" | base64 -d > /secrets/creds.json

exec python src/main.py
