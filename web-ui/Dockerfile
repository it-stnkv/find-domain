# ── Base image ──────────────────────────────────────────────
FROM python:3.11-slim

# ── System deps: whois утилита ───────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends whois && \
    rm -rf /var/lib/apt/lists/*

# ── Рабочая директория ───────────────────────────────────────
WORKDIR /app

# ── Python зависимости ───────────────────────────────────────
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ── Копируем исходники ───────────────────────────────────────
COPY main.py .
COPY index.html .
COPY domain_checker.py .

# ── Директория для данных ────────────────────────────────────
RUN mkdir -p /data

# ── Открываем порт ──────────────────────────────────────────
EXPOSE 8000

# ── Запуск ──────────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
