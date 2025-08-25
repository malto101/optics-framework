# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Accept the .whl filename as a build argument
ARG WHL_FILE
ENV WHL_FILE=${WHL_FILE}

# Copy the wheel into the container
COPY dist/${WHL_FILE} /app/
COPY Docker/dev/entrypoint.sh /app/entrypoint.sh
COPY Docker/mozark-icici.json /secrets/mozark-icici.json

# Install system dependencies and Python packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    libgl1 \
    libglib2.0-0 \
 && pip install --no-cache-dir "/app/${WHL_FILE}" \
    appium-python-client \
    google-cloud-vision \
    fastapi \
    uvicorn \
 && rm -rf /var/lib/apt/lists/* \
 && chown -R appuser:appuser /app /secrets/mozark-icici.json \
 && chmod 600 /secrets/mozark-icici.json \
 && chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

EXPOSE 8000

# Entrypoint will write GOOGLE_CREDENTIALS_JSON into a file and
# set GOOGLE_APPLICATION_CREDENTIALS before exec'ing the CMD.
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["optics", "serve", "--host", "0.0.0.0", "--port", "8000"]
