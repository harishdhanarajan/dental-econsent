FROM python:3.9-slim

# 1) Install system libs needed by WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 libcairo2-dev \
    libpango1.0-0 libpango1.0-dev \
    libgdk-pixbuf2.0-0 libgdk-pixbuf2.0-dev \
    libffi-dev build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy your application code
COPY src/ ./src

# 4) Copy and make the entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 5) Environment for Flask
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

# 6) Expose port and use entrypoint
EXPOSE 5000
CMD ["/entrypoint.sh"]
