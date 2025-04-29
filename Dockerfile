FROM python:3.12-slim

# Set environment variables to avoid Poetry virtual environments inside the container
ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy only Poetry config files first for caching
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "python", "main.py"]
