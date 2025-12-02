
#!/usr/bin/env python3
"""
RabbitMQ load test consumer using pika.
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
PERF_CONSUMERS=20
PERF_SIZE=1024
PERF_CONSUME_EXPECTED=100000   # 0 หรือไม่กำหนด = รันจนกด Ctrl+C
PERF_PREFETCH=50
PERF_ACK=1                     # 1/true = ใช้ manual ack
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


def get_bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    val_low = val.lower()
    if val_low in ("1", "true", "yes", "y", "on"):
        return True
    if val_low in ("0", "false", "no", "n", "off"):
        return False
    print(f"[WARN] ENV {name}='{val}' ไม่ใช่ค่า boolean ที่รู้จัก ใช้ default={default}")
    return default


class Counter:
    def __init__(self):
        self._lock = threading.Lock()
        self._value = 0

    def inc(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    def get(self) -> int:
        with self._lock:
            return self._value


def consumer_worker(worker_id: int,
                    url: str,
                    queue_name: str,
                    prefetch: int,
                    use_ack: bool,
                    expected: int,
                    counter: Counter,
                    stop_event: threading.Event):
    try:
        params = pika.URLParameters(url)
        conn = pika.BlockingConnection(params)
        ch = conn.channel()

        ch.queue_declare(queue=queue_name, durable=True, auto_delete=False)

        if prefetch > 0:
            ch.basic_qos(prefetch_count=prefetch)

        def callback(ch, method, properties, body):
            current = counter.inc()
            if use_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)

            if expected > 0 and current >= expected:
                stop_event.set()

        ch.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=not use_ack
        )

        while not stop_event.is_set():
            conn.process_data_events(time_limit=1)

        conn.close()
    except Exception as e:
        print(f"[Worker {worker_id}] ERROR: {e!r}")


def main():
    url = build_url()
    queue_name = os.getenv("PERF_QUEUE_NAME", "perf.test.durable")
    consumers = get_int_env("PERF_CONSUMERS", 10)
    msg_size = get_int_env("PERF_SIZE", 1024)
    expected = get_int_env("PERF_CONSUME_EXPECTED", 0)
    prefetch = get_int_env("PERF_PREFETCH", 50)
    use_ack = get_bool_env("PERF_ACK", True)

    if consumers <= 0:
        consumers = 1

    print("=== RabbitMQ Load Test Consumer (Python) ===")
    print(f"URL          : {url}")
    print(f"Queue        : {queue_name}")
    print(f"Consumers    : {consumers}")
    print(f"Prefetch     : {prefetch}")
    print(f"Ack          : {use_ack}")
    print(f"Expected msg : {expected or 'infinite (Ctrl+C)'}")
    print(f"Msg size est.: {msg_size} bytes (ใช้เพื่ออ้างอิง)")
    print("===========================================")

    counter = Counter()
    stop_event = threading.Event()
    threads = []

    start = time.perf_counter()

    for i in range(consumers):
        t = threading.Thread(
            target=consumer_worker,
            args=(i, url, queue_name, prefetch, use_ack, expected, counter, stop_event),
            daemon=True
        )
        threads.append(t)
        t.start()

    try:
        if expected > 0:
            # รอจนกว่าจะครบ expected หรือ stop_event ถูก set
            while not stop_event.is_set():
                time.sleep(0.5)
        else:
            # ไม่มี expected → รันจนกด Ctrl+C
            while True:
                time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[Main] KeyboardInterrupt, stopping consumers...")
        stop_event.set()

    for t in threads:
        t.join(timeout=2.0)

    elapsed = time.perf_counter() - start
    total = counter.get()

    print("\n=== Result Summary ===")
    print(f"Total consumed : {total}")
    print(f"Elapsed        : {elapsed:.3f} s")
    if elapsed > 0:
        print(f"Throughput     : {total / elapsed:,.0f} msg/s")


if __name__ == "__main__":
    main()
