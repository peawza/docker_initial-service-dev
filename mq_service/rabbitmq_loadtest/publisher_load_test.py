
#!/usr/bin/env python3
"""
RabbitMQ load test publisher using pika.
อ่านค่า config จาก Environment Variables (รองรับ .env ผ่าน python-dotenv)

ใช้ ENV ตามนี้ (หรือใส่ในไฟล์ .env ก็ได้):

# -------------------------
# RabbitMQ Connection Info
# -------------------------
RABBITMQ_USER=admin
RABBITMQ_PASS=P@ssw0rd
# PERF_VHOST ต้องเป็นค่าแบบ URL-encoded แล้ว
#   - vhost "/"    ให้ใช้ "%2F"
#   - vhost "mes"  ใช้ "mes" ได้เลย
PERF_VHOST=%2F

# -------------------------
# Target Host Settings
# -------------------------
PERF_SCHEME=amqp        # amqp หรือ amqps
PERF_HOST=192.168.10.105
PERF_PORT=5672

# -------------------------
# Load Test Parameters
# -------------------------
PERF_QUEUE_NAME=perf.test.durable
PERF_PRODUCERS=20
PERF_SIZE=1024
PERF_RATE=0             # 0 = ยิงเต็มแม็กซ์
PERF_TOTAL_MESSAGES=100000
"""

import os
import threading
import time

from dotenv import load_dotenv
import pika

# โหลดค่า .env (ถ้ามีไฟล์อยู่ในโฟลเดอร์เดียวกัน)
load_dotenv()


def build_url() -> str:
    user = os.getenv("RABBITMQ_USER", "admin")
    password = os.getenv("RABBITMQ_PASS", "P@ssw0rd")
    scheme = os.getenv("PERF_SCHEME", "amqp")
    host = os.getenv("PERF_HOST", "localhost")
    port = os.getenv("PERF_PORT", "5672")
    # PERF_VHOST ควรเป็น URL-encoded อยู่แล้ว เช่น "%2F"
    vhost_enc = os.getenv("PERF_VHOST", "%2F")
    return f"{scheme}://{user}:{password}@{host}:{port}/{vhost_enc}"


def get_int_env(name: str, default: int) -> int:
    val = os.getenv(name)
    if val is None or val == "":
        return default
    try:
        return int(val)
    except ValueError:
        print(f"[WARN] ENV {name}='{val}' ไม่ใช่ตัวเลข ใช้ค่า default={default} แทน")
        return default


def publisher_worker(worker_id: int,
                     url: str,
                     queue_name: str,
                     message_body: bytes,
                     total_to_send: int,
                     target_rate_per_thread: float,
                     results: dict):
    """
    worker ยิง message ไปที่ RabbitMQ
    - total_to_send: จำนวน message ที่ thread นี้ต้องส่ง
    - target_rate_per_thread: msg/s ถ้า <=0 จะยิงเต็มแม็กซ์
    """
    try:
        params = pika.URLParameters(url)
        conn = pika.BlockingConnection(params)
        ch = conn.channel()

        # queue durable (recommend สำหรับ load test แบบจริงจัง)
        ch.queue_declare(queue=queue_name, durable=True, auto_delete=False)

        # persistent messages
        props = pika.BasicProperties(delivery_mode=2)

        sent = 0
        start = time.perf_counter()

        while sent < total_to_send:
            ch.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=message_body,
                properties=props
            )
            sent += 1

            # simple rate limiting per thread
            if target_rate_per_thread > 0:
                elapsed = time.perf_counter() - start
                ideal_elapsed = sent / target_rate_per_thread
                if ideal_elapsed > elapsed:
                    time.sleep(ideal_elapsed - elapsed)

        elapsed_total = time.perf_counter() - start
        conn.close()

        results[worker_id] = {"sent": sent, "elapsed": elapsed_total, "error": None}
    except Exception as e:
        results[worker_id] = {"sent": 0, "elapsed": 0.0, "error": repr(e)}


def main():
    url = build_url()
    queue_name = os.getenv("PERF_QUEUE_NAME", "perf.test.durable")
    producers = get_int_env("PERF_PRODUCERS", 10)
    msg_size = get_int_env("PERF_SIZE", 1024)
    total_messages = get_int_env("PERF_TOTAL_MESSAGES", 100_000)
    target_rate = get_int_env("PERF_RATE", 0)  # msg/s ทั้งระบบ, 0 = unlimited

    if producers <= 0:
        producers = 1

    message_body = b"x" * msg_size

    print("=== RabbitMQ Load Test Publisher (Python) ===")
    print(f"URL          : {url}")
    print(f"Queue        : {queue_name}")
    print(f"Producers    : {producers}")
    print(f"Total msg    : {total_messages}")
    print(f"Msg size     : {msg_size} bytes")
    print(f"Target rate  : {target_rate} msg/s (0 = unlimited)")
    print("=============================================")

    # แบ่ง message ให้แต่ละ producer
    base = total_messages // producers
    remainder = total_messages % producers

    results = {}
    threads = []

    if target_rate > 0:
        target_per_thread = target_rate / producers
    else:
        target_per_thread = 0.0

    global_start = time.perf_counter()

    for i in range(producers):
        count = base + (1 if i < remainder else 0)
        t = threading.Thread(
            target=publisher_worker,
            args=(i, url, queue_name, message_body, count, target_per_thread, results),
            daemon=True
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    global_elapsed = time.perf_counter() - global_start

    total_sent = 0
    max_thread_time = 0.0
    errors = []

    for worker_id, res in results.items():
        sent = res["sent"]
        elapsed = res["elapsed"]
        err = res["error"]
        total_sent += sent
        if elapsed > max_thread_time:
            max_thread_time = elapsed
        if err:
            errors.append((worker_id, err))

    print("\n=== Result Summary ===")
    print(f"Total sent        : {total_sent}")
    print(f"Wall time (global): {global_elapsed:.3f} s")
    print(f"Max thread time   : {max_thread_time:.3f} s")

    if global_elapsed > 0:
        msg_per_sec = total_sent / global_elapsed
        mb_per_sec = (total_sent * msg_size) / (1024 * 1024 * global_elapsed)
        print(f"Throughput        : {msg_per_sec:,.0f} msg/s")
        print(f"Data rate         : {mb_per_sec:,.2f} MB/s")

    if errors:
        print("\nErrors:")
        for wid, err in errors:
            print(f"  Worker {wid}: {err}")


if __name__ == "__main__":
    main()
