import json
import time
from datetime import datetime, timezone

counter = 1
while True:
    is_error = counter % 5 == 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    method = "POST" if is_error else "GET"
    path = "/api/orders"
    status_code = 500 if is_error else 200
    request_size_kb = 3.4 if is_error else 1.8
    response_size_kb = 2.1 if is_error else 4.7
    exception = "System.TimeoutException: upstream service timeout" if is_error else ""

    request_payload = {
        "headers": {
            "x-correlation-id": f"req-{counter:08d}",
            "content-type": "application/json",
        },
        "query": {
            "page": 1,
            "limit": 20,
        },
        "body": {
            "customerId": f"CUST-{1000 + counter}",
        },
    }

    response_payload = {
        "status": status_code,
        "elapsedMs": 850 if is_error else 120,
        "result": "error" if is_error else "ok",
    }

    payload = {
        "@timestamp": now,
        "Id": counter,
        "Timestamp": now,
        "Level": "Error" if is_error else "Information",
        "Message": f"{method} {path} {status_code}",
        "Request": json.dumps(request_payload, ensure_ascii=False),
        "Response": json.dumps(response_payload, ensure_ascii=False),
        "Path": path,
        "Method": method,
        "StatusCode": status_code,
        "RequestSizeKb": request_size_kb,
        "ResponseSizeKb": response_size_kb,
        "Exception": exception,
        "tag": "docker.api.calls",
    }
    print(json.dumps(payload), flush=True)
    counter += 1
    time.sleep(3)
