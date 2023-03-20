# Roadmap (2023)

Goals for Server Monitoring (FastAPI + psutil + Prometheus), organized by 2023 quarters.

Q1 2023
- Basic endpoints: `/health`, `/metrics/json`, `/metrics`.
- Metric snapshot: CPU/RAM/Disk/Net.
- Minimal configuration and `uvicorn` run.

Q2 2023
- Add system metrics: per-disk load, top processes.
- Export extra metrics: file descriptors, uptime.
- Tests: `pytest` for collectors and endpoints.

Q3 2023
- CI: GitHub Actions (Python 3.13), linters (`ruff`, `black`, `mypy`).
- Observability: structured logging, `/metrics` improvements.
- Configuration: `pydantic-settings`, intervals and filters.

Q4 2023
- Integration with Prometheus/Grafana: example dashboard, compose.
- Security: access limits, rate limiting, CORS.
- Performance: profiling, optimizing metric collection.

Technical Notes
- Use `psutil` for cross-platform collection.
- Name metrics in Prometheus style, include units in names.
- Stateless service, scale horizontally.