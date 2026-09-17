"""Lightweight authenticated API load check.
Usage:
  python scripts/load_test.py --base-url http://localhost:8000 --email admin@example.com --password admin123 --path /health/ready

The script reports p50/p95/p99 latency and error rate. A passing result is <=3s p95 and 0% HTTP errors.
It is a validation tool, not a production load-testing framework.
"""
import argparse
import json
import statistics
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def post_form(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode())


def request_once(url, token=None):
    headers = {"Authorization": f"Bearer {token}" } if token else {}
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()
            return (time.perf_counter() - start) * 1000, response.status, None
    except Exception as exc:
        return (time.perf_counter() - start) * 1000, 0, str(exc)


def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    index = min(len(values) - 1, round((p / 100) * (len(values) - 1)))
    return values[index]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--email", default="admin@example.com")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--path", default="/health/ready")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()

    token = None
    if args.path.startswith("/performance") or args.path.startswith("/dashboard"):
        payload = post_form(f"{args.base_url}/login", {"username": args.email, "password": args.password})
        token = payload["access_token"]

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(request_once, f"{args.base_url}{args.path}", token) for _ in range(args.requests)]
        results = [future.result() for future in as_completed(futures)]

    latencies = [r[0] for r in results]
    errors = sum(1 for r in results if r[2] or r[1] >= 500)
    print(f"Requests: {len(results)}")
    print(f"Errors: {errors} ({errors / len(results) * 100:.2f}%)")
    print(f"p50: {percentile(latencies, 50):.1f} ms")
    print(f"p95: {percentile(latencies, 95):.1f} ms")
    print(f"p99: {percentile(latencies, 99):.1f} ms")
    passed = errors == 0 and percentile(latencies, 95) <= 3000
    print("RESULT:", "PASS" if passed else "FAIL")
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
