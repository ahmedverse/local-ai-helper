FROM ghcr.io/danny-avila/librechat:latest

# Switch to root to install system dependencies
USER root

# Install git and python using Alpine's package manager (apk)
RUN apk update && apk add --no-cache \
    git \
    python3 \
    py3-pip

# Install Python packages required for your MCP server (pinned to mcp v1)
RUN pip install --no-cache-dir --break-system-packages "mcp<2" requests python-dotenv

# Switch back to the non-root user (node)
USER node