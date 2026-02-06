#!/bin/bash
set -e

# Generate SearXNG secret if set to auto
if [ "$SEARXNG_SECRET" = "auto" ]; then
    export SEARXNG_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
fi

# Patch SearXNG settings with runtime secret
if [ -f /etc/searxng/settings.yml ]; then
    sed -i "s/secret_key: .*/secret_key: \"${SEARXNG_SECRET}\"/" /etc/searxng/settings.yml
fi

# Ensure data directories exist
mkdir -p /data/surrealdb /app/downloads /app/data /var/log/supervisor

echo "=== Paper Search MCP — All-in-One ==="
echo "  MCP Server:  port 3000"
echo "  SurrealDB:   port 8000"
echo "  SearXNG:     port 8080"
echo "======================================"

exec "$@"
