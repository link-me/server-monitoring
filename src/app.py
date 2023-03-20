import os
import time
import psutil
from fastapi import FastAPI
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


app = FastAPI(title="Server Monitoring API")


def snapshot_metrics():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    return {
        "timestamp": int(time.time()),
        "cpu_percent": cpu_percent,
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "percent": mem.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "percent": disk.percent,
        },
        "net": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics/json")
def metrics_json():
    return snapshot_metrics()


@app.get("/metrics")
def metrics_prom():
    reg = CollectorRegistry()
    g_cpu = Gauge("system_cpu_percent", "CPU usage percent", registry=reg)
    g_mem_used = Gauge("system_memory_used_bytes", "Memory used in bytes", registry=reg)
    g_mem_total = Gauge("system_memory_total_bytes", "Memory total in bytes", registry=reg)
    g_disk_used = Gauge("system_disk_used_bytes", "Disk used in bytes", registry=reg)
    g_disk_total = Gauge("system_disk_total_bytes", "Disk total in bytes", registry=reg)
    g_net_sent = Gauge("system_net_bytes_sent", "Network bytes sent", registry=reg)
    g_net_recv = Gauge("system_net_bytes_recv", "Network bytes received", registry=reg)

    snap = snapshot_metrics()
    g_cpu.set(snap["cpu_percent"])
    g_mem_used.set(snap["memory"]["used"])
    g_mem_total.set(snap["memory"]["total"])
    g_disk_used.set(snap["disk"]["used"])
    g_disk_total.set(snap["disk"]["total"])
    g_net_sent.set(snap["net"]["bytes_sent"])
    g_net_recv.set(snap["net"]["bytes_recv"])

    output = generate_latest(reg)
    return Response(content=output, media_type=CONTENT_TYPE_LATEST)


def get_port() -> int:
    try:
        return int(os.getenv("PORT", "8030"))
    except Exception:
        return 8030