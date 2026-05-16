# ──────────────────────────────────────────────
# FinSense: Level 5 Autonomous Quant Agent
# ──────────────────────────────────────────────

# Base Image: Python 3.11 slim (lightweight, production-grade)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# ── System Dependencies ──────────────────────
# Required for yfinance and some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python Dependencies ──────────────────────
# Copy requirements first for Docker layer caching
# (only reinstalls if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Application Code ─────────────────────────
COPY . .

# ── Environment Variables ─────────────────────
# GROQ_API_KEY must be passed at runtime:
# docker run -e GROQ_API_KEY=your_key ...
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

# ── Security: Non-root user ───────────────────
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# ── Expose Gradio Port ────────────────────────
EXPOSE 7860

# ── Health Check ─────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860 || exit 1

# ── Start the App ─────────────────────────────
CMD ["python", "main.py"]
