# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies. Pin them so a Container App revision built
# next month resolves to the same versions as the one built today.
COPY lesson9/src/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Bake the current prompt version into the image. The deploy workflow triggers
# on prompts/** so a new prompt file produces a new image + new revision.
COPY lesson9/prompts /app/prompts

# Application code.
COPY lesson9/src/api /app/api

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
