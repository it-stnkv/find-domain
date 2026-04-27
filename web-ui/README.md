# Domain Checker

<img width="910" height="1046" alt="image" src="https://github.com/user-attachments/assets/dbcabd25-08a9-4e2f-b564-d5626588ac9b" />

Bulk WHOIS availability scanner with Web UI.

## Quick Start

### With Docker Compose (recommended)
```bash
docker-compose up --build
```
Open: http://localhost:8000

### With Docker only
```bash
docker build -t domain-checker .
docker run -p 8000:8000 -v $(pwd)/data:/data domain-checker
```

## Manual run (without Docker)
```bash
pip3 install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Usage
1. Open http://localhost:8000
2. Upload your domains.csv
3. Click Run Check
4. Download results.csv
