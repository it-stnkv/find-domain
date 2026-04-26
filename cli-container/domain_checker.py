import csv
import time
import subprocess
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


# =========================
# CONFIG
# =========================
INPUT_FILE = "/data/domains.csv"
OUTPUT_FILE = "/data/results.csv"

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

            # --- признаки свободного домена ---
            if any(keyword in output for keyword in [
                "no match",
                "not found",
                "no data found",
                "status: free",
                "available"
            ]):
                return domain, "Available"

            # если ответ есть — считаем занятым
            if output.strip():
                return domain, "Taken"

            return domain, "Error"

        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {domain}")
            if attempt < RETRIES - 1:
                time.sleep(1)
                continue
            return domain, "Error"

        except Exception as e:
            print(f"[ERROR] {domain}: {e}")
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

        rows = []
        for row in reader:
            cleaned_row = [clean_string(cell) for cell in row]
            if any(cleaned_row):
                rows.append(cleaned_row)

    if not rows:
        raise ValueError("CSV файл пуст")

    header = [h.lower() for h in rows[0]]
    possible_keys = ["domain", "domains", "domain name"]

    if any(key in header for key in possible_keys):
        print("📊 Detected CSV with header")

        column_index = None
        for i, col in enumerate(header):
            if col in possible_keys:
                column_index = i
                break

        if column_index is None:
            raise ValueError("Header detected but no valid domain column found")

        for row in rows[1:]:
            if len(row) > column_index and row[column_index]:
                domains.append(row[column_index])

    else:
        print("📄 Detected CSV without header")
        for row in rows:
            if row and row[0]:
                domains.append(row[0])

    # сохраняем порядок + убираем дубли
    domains = list(dict.fromkeys(d.strip() for d in domains if d.strip()))

    print(f"✅ Loaded {len(domains)} domains")

    if not domains:
        raise ValueError("No valid domains found in CSV")

    return domains


def write_results(results: List[Tuple[str, str]], file_path: str):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain Name", "Status"])
        writer.writerows(results)


# =========================
# MAIN PROCESSOR
# =========================
def process_domains(domains: List[str]) -> List[Tuple[str, str]]:
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_domain, d): d for d in domains}

        for future in tqdm(as_completed(futures), total=len(domains)):
            domain = futures[future]
            try:
                results.append(future.result(timeout=TIMEOUT + 5))
            except Exception as e:
                print(f"[FUTURE ERROR] {domain}: {e}")
                results.append((domain, "Error"))

    return results


# =========================
# ENTRY POINT
# =========================
def main():
    print("📥 Reading domains...")
    domains = read_domains(INPUT_FILE)

    print(f"🚀 Checking {len(domains)} domains...")
    results = process_domains(domains)

    print("💾 Writing results...")
    write_results(results, OUTPUT_FILE)

    print("✅ Done!")


if __name__ == "__main__":
    main()
