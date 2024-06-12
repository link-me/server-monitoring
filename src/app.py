import os
import time
import psutil
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Server Monitoring — Matrix Admin</title>
  <style>
    :root {
      --bg: #0b0f10;
      --panel: #10161a;
      --primary: #00ff95;
      --accent: #39ff14;
      --muted: #7fffb2;
      --danger: #ff3860;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0; background: var(--bg); color: var(--primary);
      font-family: Consolas, Monaco, 'Courier New', monospace;
    }
    .grid {
      max-width: 1100px; margin: 32px auto; padding: 0 16px;
      display: grid; grid-template-columns: repeat(12, 1fr); grid-gap: 16px;
    }
    .card {
      grid-column: span 4; background: linear-gradient(180deg, #0d1317 0%, var(--panel) 100%);
      border: 1px solid #143026; border-radius: 10px; padding: 16px; box-shadow: 0 8px 24px rgba(0,255,149,0.05);
    }
    .card h3 { margin: 0 0 8px; color: var(--accent); font-weight: 600; letter-spacing: 0.5px; }
    .row { display: flex; align-items: center; justify-content: space-between; margin: 6px 0; }
    .mono { color: var(--muted); }
    .bar {
      position: relative; height: 10px; background: #0a1410; border: 1px solid #143026; border-radius: 6px; overflow: hidden;
    }
    .bar > span { display: block; height: 100%; background: linear-gradient(90deg, #0ee48a, #39ff14); width: 0%; }
    .footer { text-align: center; opacity: 0.8; margin: 12px 0 32px; font-size: 12px; color: #62ffa7; }
    .header { text-align: center; padding: 18px 16px; }
    .header h1 { margin: 0; font-size: 20px; font-weight: 700; color: var(--accent); }
    .blink { animation: blink 1.6s infinite; }
    @keyframes blink { 50% { opacity: 0.35; } }
    .small { font-size: 12px; opacity: 0.85; }
    .danger { color: var(--danger); }
  </style>
</head>
<body>
  <div class="header">
    <h1>Server Monitoring <span class="small mono">— Matrix Admin</span> <span class="blink">▮</span></h1>
  </div>
  <div class="grid">
    <div class="card" id="cpu">
      <h3>CPU</h3>
      <div class="row"><span class="mono">Usage</span><span id="cpu_pct">—</span></div>
      <div class="bar"><span id="cpu_bar"></span></div>
    </div>
    <div class="card" id="mem">
      <h3>Memory</h3>
      <div class="row"><span class="mono">Used</span><span id="mem_used">—</span></div>
      <div class="row"><span class="mono">Total</span><span id="mem_total">—</span></div>
      <div class="row"><span class="mono">Percent</span><span id="mem_pct">—</span></div>
      <div class="bar"><span id="mem_bar"></span></div>
    </div>
    <div class="card" id="disk">
      <h3>Disk</h3>
      <div class="row"><span class="mono">Used</span><span id="disk_used">—</span></div>
      <div class="row"><span class="mono">Total</span><span id="disk_total">—</span></div>
      <div class="row"><span class="mono">Percent</span><span id="disk_pct">—</span></div>
      <div class="bar"><span id="disk_bar"></span></div>
    </div>
    <div class="card" id="net">
      <h3>Network</h3>
      <div class="row"><span class="mono">Bytes Sent</span><span id="net_sent">—</span></div>
      <div class="row"><span class="mono">Bytes Recv</span><span id="net_recv">—</span></div>
    </div>
    <div class="card" id="meta">
      <h3>Meta</h3>
      <div class="row"><span class="mono">Timestamp</span><span id="ts">—</span></div>
      <div class="row"><span class="mono">Refresh</span><span class="small mono">2s auto</span></div>
    </div>
  </div>
  <div class="footer">Prometheus endpoint: <a href="/metrics" target="_blank" style="color: var(--accent)">/metrics</a></div>

  <script>
    const fmtBytes = (n) => {
      const u = ['B','KB','MB','GB','TB'];
      let i = 0; let v = n;
      while (v >= 1024 && i < u.length-1) { v /= 1024; i++; }
      return `${v.toFixed(1)} ${u[i]}`;
    };
    const setBar = (el, pct) => { el.style.width = `${Math.min(100, Math.max(0, pct))}%`; };
    async function load() {
      try {
        const res = await fetch('/metrics/json');
        const j = await res.json();
        document.getElementById('cpu_pct').textContent = `${j.cpu_percent.toFixed(1)}%`;
        setBar(document.getElementById('cpu_bar'), j.cpu_percent);

        document.getElementById('mem_used').textContent = fmtBytes(j.memory.used);
        document.getElementById('mem_total').textContent = fmtBytes(j.memory.total);
        document.getElementById('mem_pct').textContent = `${j.memory.percent.toFixed(1)}%`;
        setBar(document.getElementById('mem_bar'), j.memory.percent);

        document.getElementById('disk_used').textContent = fmtBytes(j.disk.used);
        document.getElementById('disk_total').textContent = fmtBytes(j.disk.total);
        document.getElementById('disk_pct').textContent = `${j.disk.percent.toFixed(1)}%`;
        setBar(document.getElementById('disk_bar'), j.disk.percent);

        document.getElementById('net_sent').textContent = fmtBytes(j.net.bytes_sent);
        document.getElementById('net_recv').textContent = fmtBytes(j.net.bytes_recv);

        document.getElementById('ts').textContent = new Date(j.timestamp*1000).toLocaleString();
      } catch (e) {
        console.error(e);
      }
    }
    load();
    setInterval(load, 2000);
  </script>
</body>
</html>
"""