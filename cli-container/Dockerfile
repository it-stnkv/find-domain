# =========================
# STAGE 1: base
# =========================
FROM python:3.11-slim

# отключаем буферизацию
ENV PYTHONUNBUFFERED=1

# рабочая директория
WORKDIR /app

# =========================
# SYSTEM DEPENDENCIES
# =========================
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        whois \
    && rm -rf /var/lib/apt/lists/*

# =========================
# PYTHON DEPENDENCIES
# =========================
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# =========================
# APP
# =========================
COPY domain_checker.py .

# =========================
# ENTRYPOINT
# =========================
CMD ["python3", "domain_checker.py"]
