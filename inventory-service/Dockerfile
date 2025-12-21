FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl for poetry)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency definition
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev dependencies, no interaction)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Run the application
# We use shell variable expansion for the port, defaulting to the standard if not set
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8000}"]