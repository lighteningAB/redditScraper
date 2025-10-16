# Use official lightweight Python image
FROM python:3.11-slim

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       git \
       libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Streamlit listens on port 8501 by default, but Vercel provides $PORT
EXPOSE 8501

# Ensure Streamlit runs on 0.0.0.0 and uses the PORT env var when provided
ENV STREAMLIT_SERVER_HEADLESS=true

# Default command: use $PORT if set, otherwise 8501
CMD ["bash", "-lc", "streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
