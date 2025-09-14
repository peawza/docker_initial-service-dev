import os, json
from flask import Flask, request, redirect, url_for
import boto3
from botocore.config import Config
from datetime import datetime, timedelta

REGION = os.getenv("AWS_REGION", "ap-southeast-1")
ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")

cfg = Config(region_name=REGION, signature_version="v4")
lambda_client = boto3.client("lambda", endpoint_url=ENDPOINT, config=cfg)
logs_client   = boto3.client("logs",   endpoint_url=ENDPOINT, config=cfg)
apigw_client  = boto3.client("apigateway", endpoint_url=ENDPOINT, config=cfg)

app = Flask(__name__)

def html_page(title, body):
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:ui-sans-serif,system-ui,Segoe UI,Arial;padding:24px;max-width:1000px;margin:auto}}
a{{text-decoration:none}} table{{border-collapse:collapse}} td,th{{border:1px solid #ddd;padding:6px 8px}} 
code,pre{{background:#f6f6f6;padding:4px 6px;border-radius:6px}}
.btn{{display:inline-block;padding:6px 10px;border:1px solid #444;border-radius:6px;margin-right:8px}}</style>
</head><body>
<h2>{title}</h2>
<div style="margin-bottom:16px">
  <a class="btn" href="/">Home</a>
  <a class="btn" href="/lambda">Lambda</a>
  <a class="btn" href="/logs">CloudWatch Logs</a>
  <a class="btn" href="/apigw">API Gateway</a>
</div>
{body}
</body></html>"""

@app.get("/")
def home():
    body = f"""
<p>Connected to LocalStack at <code>{ENDPOINT}</code> (region <b>{REGION}</b>)</p>
<ul>
  <li><a href="/lambda">Browse &amp; invoke Lambda</a></li>
  <li><a href="/logs">Browse CloudWatch Log groups/streams</a></li>
  <li><a href="/apigw">List REST APIs &amp; resources</a></li>
</ul>
"""
    return html_page("Local AWS UI (Community)", body)

# ---------- Lambda ----------
@app.get("/lambda")
def list_lambda():
    funcs = lambda_client.list_functions().get("Functions", [])
    rows = "".join(
        f"<tr><td>{f['FunctionName']}</td>"
        f"<td>{f.get('Runtime','')}</td>"
        f"<td><a class='btn' href='/lambda/invoke/{f['FunctionName']}'>Invoke</a></td></tr>"
        for f in funcs
    )
    if not rows: rows = "<tr><td colspan=3>No functions</td></tr>"
    body = f"<table><tr><th>Name</th><th>Runtime</th><th>Action</th></tr>{rows}</table>"
    return html_page("Lambda", body)

@app.get("/lambda/invoke/<name>")
def invoke_lambda(name):
    try:
        res = lambda_client.invoke(FunctionName=name, Payload=b'{"ping":true}')
        payload = res["Payload"].read().decode("utf-8")
    except Exception as e:
        payload = f"ERROR: {e}"
    body = f"<p>Invoke <b>{name}</b></p><pre>{payload}</pre>"
    return html_page(f"Invoke {name}", body)

# ---------- CloudWatch Logs ----------
@app.get("/logs")
def list_log_groups():
    groups = logs_client.describe_log_groups(limit=50).get("logGroups", [])
    rows = "".join(
        f"<tr><td>{g['logGroupName']}</td>"
        f"<td><a class='btn' href='/logs/group?name={g['logGroupName']}'>Open</a></td></tr>"
        for g in groups
    )
    if not rows: rows = "<tr><td colspan=2>No log groups</td></tr>"
    body = f"<table><tr><th>Log Group</th><th>Action</th></tr>{rows}</table>"
    return html_page("CloudWatch Logs", body)

@app.get("/logs/group")
def view_group():
    name = request.args.get("name")
    streams = logs_client.describe_log_streams(logGroupName=name, orderBy="LastEventTime", descending=True, limit=20).get("logStreams", [])
    rows = "".join(
        f"<tr><td>{s['logStreamName']}</td>"
        f"<td>{s.get('lastEventTimestamp','')}</td>"
        f"<td><a class='btn' href='/logs/stream?group={name}&stream={s['logStreamName']}'>Tail</a></td></tr>"
        for s in streams
    )
    if not rows: rows = "<tr><td colspan=3>No streams</td></tr>"
    body = f"<p>Group: <b>{name}</b></p><table><tr><th>Stream</th><th>LastEvent</th><th>Action</th></tr>{rows}</table>"
    return html_page(f"Logs: {name}", body)

@app.get("/logs/stream")
def view_stream():
    group = request.args.get("group")
    stream = request.args.get("stream")
    # โหลด events ล่าสุด (15 นาที)
    start = int((datetime.utcnow() - timedelta(minutes=15)).timestamp() * 1000)
    events = logs_client.get_log_events(logGroupName=group, logStreamName=stream, startTime=start, limit=200).get("events", [])
    rows = "\n".join(f"[{datetime.utcfromtimestamp(e['timestamp']/1000).isoformat()}] {e['message']}" for e in events)
    body = f"<p>Group: <b>{group}</b> / Stream: <b>{stream}</b></p><pre>{rows or 'No events'}</pre>"
    return html_page(f"Logs: {group}/{stream}", body)

# ---------- API Gateway ----------
@app.get("/apigw")
def list_apigw():
    apis = apigw_client.get_rest_apis(limit=50).get("items", [])
    rows = ""
    for a in apis:
        rid = a["id"]
        # list root resources
        res = apigw_client.get_resources(restApiId=rid).get("items", [])
        paths = ", ".join(sorted(set([r.get("path","/") for r in res])))
        url = f"http://localhost:4566/restapis/{rid}/dev/_user_request_/"  # default stage dev (ถ้ามี)
        rows += f"<tr><td>{a['name']}</td><td>{rid}</td><td>{paths}</td><td><a class='btn' href='{url}'>Try (dev)</a></td></tr>"
    if not rows: rows = "<tr><td colspan=4>No REST APIs</td></tr>"
    body = f"<table><tr><th>Name</th><th>ID</th><th>Paths</th><th>Action</th></tr>{rows}</table>"
    return html_page("API Gateway (REST)", body)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
