# DSL Schema Tools Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir jsonschema pyyaml requests

# Copy application code
COPY ../Tools/ ./Tools/

# Set environment variables
ENV PYTHONPATH=/app

# Run as non-root user
RUN useradd -m -u 1000 schemauser
USER schemauser

# Default command
CMD ["python", "-m", "Tools.schema_validator", "--help"]
