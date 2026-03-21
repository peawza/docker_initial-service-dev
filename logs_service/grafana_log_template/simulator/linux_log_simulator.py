import json
import random
import time
from datetime import datetime, timezone

messages = [
    ("Information", "systemd started sshd service", "systemd"),
    ("Information", "cron job completed", "cron"),
    ("Warning", "disk usage reached 82%", "kernel"),
    ("Warning", "high load average detected", "kernel"),
    ("Error", "failed to rotate logs due to permission denied", "rsyslog"),
]

while True:
    level, message, service = random.choice(messages)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    log = {
        "Timestamp": now,
        "Level": level,
        "Message": message,
        "Host": "linux-node-01",
        "Service": service,
    }

    with open("/simulator/logs/linux.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    time.sleep(3)
