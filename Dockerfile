# File: Dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy source
COPY . .

EXPOSE 7860
CMD ["uv", "run", "main.py"]
