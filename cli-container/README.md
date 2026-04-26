# Domain Checker (Docker)

CLI tool for checking domain availability using WHOIS.

## Requirements

- Docker installed

## Prepare data

Create a directory and place your `domains.csv` file:
data/
└── domains.csv

Example:
```csv
domain
example.com
example.dev
example.io
```

## Run container
```bash
docker run --rm \
  -v $(pwd)/data:/data \
  domain-checker
```

## Output file

After execution, results will be available in:
`data/results.csv`

## Notes
Input file must be /data/domains.csv
Output file will be /data/results.csv
WHOIS servers may rate limit requests
Adjust concurrency in code if needed:
```python
MAX_WORKERS = 5
REQUEST_DELAY = 1
```

## Build manually
```bash
docker build -t domain-checker .
```

## If problem:
dns
```bash
docker run --rm busybox nslookup google.com
```

file rules:
```bash
chmod -R 777 data
```

