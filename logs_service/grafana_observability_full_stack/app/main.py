import json
import logging
import os
import random
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


def init_tracer() -> trace.Tracer:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector:4317")
    resource = Resource(attributes={SERVICE_NAME: "debug-api"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(provider)
    return trace.get_tracer("debug-api-tracer")


def init_logger() -> logging.Logger:
    logger = logging.getLogger("debug-api")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    log_file = os.getenv("APP_LOG_FILE", "/tmp/app.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_DURATION = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request duration seconds",
    ["method", "path", "status"],
    buckets=(0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0),
)

app = FastAPI(title="debug-api", version="1.0.0")
tracer = init_tracer()
logger = init_logger()


def write_log(level: str, message: str, request: Request, status_code: int, exception: str = "") -> None:
    span = trace.get_current_span()
    span_ctx = span.get_span_context()
    trace_id = format(span_ctx.trace_id, "032x") if span_ctx.is_valid else ""
    span_id = format(span_ctx.span_id, "016x") if span_ctx.is_valid else ""

    payload = {
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Level": level,
        "Message": message,
        "Path": request.url.path,
        "Method": request.method,
        "StatusCode": status_code,
        "Exception": exception,
        "trace_id": trace_id,
        "span_id": span_id,
        "service": "debug-api",
    }
    logger.info(json.dumps(payload, ensure_ascii=False))


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    start = time.time()
    status_code = 500

    with tracer.start_as_current_span(f"{request.method} {request.url.path}") as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.target", request.url.path)

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as ex:
            write_log("Error", str(ex), request, 500, exception=str(ex))
            raise
        finally:
            duration = time.time() - start
            REQUEST_COUNT.labels(request.method, request.url.path, str(status_code)).inc()
            REQUEST_DURATION.labels(request.method, request.url.path, str(status_code)).observe(duration)
            span.set_attribute("http.status_code", status_code)
            span.set_attribute("http.response_time_ms", duration * 1000)


@app.get("/ok")
def ok(request: Request):
    write_log("Information", "ok endpoint served", request, 200)
    return {"status": "ok"}


@app.get("/slow")
def slow(request: Request):
    delay = random.uniform(0.6, 2.5)
    time.sleep(delay)
    write_log("Warning", f"slow endpoint delay={delay:.2f}s", request, 200)
    return {"status": "slow", "delay": delay}


@app.get("/error")
def error(request: Request):
    write_log("Error", "simulated 500 error", request, 500, exception="RuntimeError: simulated failure")
    raise HTTPException(status_code=500, detail="simulated failure")


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
