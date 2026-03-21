import json
import random
import time
from datetime import datetime, timezone

counter = 1

while True:
    is_error = counter % 6 == 0
    method = random.choice(["GET", "POST", "PUT", "DELETE"])
    path = random.choice([
        "/api/orders",
        "/api/orders/summary",
        "/api/customers",
        "/api/invoices",
    ])
    status_code = 500 if is_error else random.choice([200, 200, 201, 204, 400])
    level = "Error" if status_code >= 500 else "Warning" if status_code >= 400 else "Information"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    request_size_kb = round(random.uniform(1.0, 12.0), 2)
    response_size_kb = round(random.uniform(0.8, 18.0), 2)
    exception = "System.TimeoutException: upstream timeout" if is_error else ""

    req = {
        "headers": {
            "x-correlation-id": f"req-{counter:08d}",
            "content-type": "application/json",
        },
        "query": {
            "page": random.randint(1, 5),
            "limit": 20,
        },
        "body": {
            "customerId": f"CUST-{1000 + counter}",
            "amount": random.randint(100, 2000),
        },
    }

    res = {
        "status": status_code,
        "elapsedMs": random.randint(40, 1200),
        "result": "error" if status_code >= 400 else "ok",
    }

    log = {
        "Id": counter,
        "Timestamp": now,
        "Level": level,
        "Message": f"{method} {path} {status_code}",
        "Request": json.dumps(req, ensure_ascii=False),
        "Response": json.dumps(res, ensure_ascii=False),
        "Path": path,
        "Method": method,
        "StatusCode": status_code,
        "RequestSizeKb": request_size_kb,
        "ResponseSizeKb": response_size_kb,
        "Exception": exception,
    }

    with open("/simulator/logs/api.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    counter += 1
    time.sleep(2)
