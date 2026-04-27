import os
import csv
import time
import subprocess
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# =========================
# APP SETUP
# =========================
app = FastAPI(title="Domain Checker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "/data"
INPUT_FILE = os.path.join(DATA_DIR, "domains.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "results.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# CONFIG
# =========================
MAX_WORKERS = 10
REQUEST_DELAY = 0.5
RETRIES = 3
TIMEOUT = 10


# =========================
# WHOIS LOGIC
# =========================
def check_domain(domain: str) -> Tuple[str, str]:
    for attempt in range(RETRIES):
        try:
            result = subprocess.run(
                ["whois", domain],
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )
            output = result.stdout.lower()

            if any(keyword in output for keyword in [
                "no match", "not found", "no data found", "status: free", "available"
            ]):
                return domain, "Available"

            if output.strip():
                return domain, "Taken"

            return domain, "Error"

        except subprocess.TimeoutExpired:
            if attempt < RETRIES - 1:
                time.sleep(1)
                continue
            return domain, "Error"

        except Exception:
            return domain, "Error"

        finally:
            time.sleep(REQUEST_DELAY)

    return domain, "Error"


# =========================
# CSV HANDLING
# =========================
def clean_string(value: str) -> str:
    return value.strip().replace("\ufeff", "")


def read_domains(file_path: str) -> List[str]:
    domains = []

    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = [[clean_string(cell) for cell in row] for row in reader if any(row)]

    if not rows:
        raise ValueError("CSV file is empty")

    header = [h.lower() for h in rows[0]]
    possible_keys = ["domain", "domains", "domain name"]

    if any(key in header for key in possible_keys):
        column_index = next((i for i, col in enumerate(header) if col in possible_keys), None)
        if column_index is None:
            raise ValueError("No valid domain column found")
        for row in rows[1:]:
            if len(row) > column_index and row[column_index]:
                domains.append(row[column_index])
    else:
        for row in rows:
            if row and row[0]:
                domains.append(row[0])

    domains = list(dict.fromkeys(d.strip() for d in domains if d.strip()))

    if not domains:
        raise ValueError("No valid domains found in CSV")

    return domains


def write_results(results: List[Tuple[str, str]], file_path: str):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain Name", "Status"])
        writer.writerows(results)


def process_domains(domains: List[str]) -> List[Tuple[str, str]]:
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_domain, d): d for d in domains}
        for future in as_completed(futures):
            domain = futures[future]
            try:
                results.append(future.result(timeout=TIMEOUT + 5))
            except Exception:
                results.append((domain, "Error"))
    return results


# =========================
# API ENDPOINTS
# =========================
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    with open(INPUT_FILE, "wb") as f:
        f.write(content)

    return JSONResponse({"status": "ok", "message": f"Uploaded: {file.filename}"})


@app.post("/run")
async def run_check():
    if not os.path.exists(INPUT_FILE):
        raise HTTPException(status_code=404, detail="No input file found. Please upload domains.csv first.")

    try:
        domains = read_domains(INPUT_FILE)
        results = process_domains(domains)
        write_results(results, OUTPUT_FILE)

        total = len(results)
        available = sum(1 for _, s in results if s == "Available")
        taken = sum(1 for _, s in results if s == "Taken")
        errors = sum(1 for _, s in results if s == "Error")

        return JSONResponse({
            "status": "ok",
            "total": total,
            "available": available,
            "taken": taken,
            "errors": errors
        })
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/download")
async def download_results():
    if not os.path.exists(OUTPUT_FILE):
        raise HTTPException(status_code=404, detail="No results file found. Please run a check first.")

    return FileResponse(
        path=OUTPUT_FILE,
        media_type="text/csv",
        filename="results.csv"
    )

# (опционально):
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
