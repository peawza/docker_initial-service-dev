import random
import time

import requests

TARGET = "http://debug-api:8080"
ENDPOINTS = ["/ok", "/ok", "/slow", "/error"]

while True:
    path = random.choice(ENDPOINTS)
    try:
        requests.get(TARGET + path, timeout=5)
    except requests.RequestException:
        pass
    time.sleep(0.7)
