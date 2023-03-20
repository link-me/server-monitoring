# Server Monitoring

Server Monitoring API на FastAPI, отдаёт системные метрики и экспортирует их в формате Prometheus.

Стек
- FastAPI — HTTP API.
- psutil — сбор системных метрик (CPU/RAM/Disk/Net).
- prometheus-client — экспорт метрик на `/metrics`.
- uvicorn — dev‑сервер.

Быстрый старт
1. Создать окружение и установить зависимости:
   - `python -m venv .venv && .venv\Scripts\activate`
   - `pip install -r requirements.txt`
2. Запуск: `uvicorn src.app:app --host 127.0.0.1 --port 8030`
3. Эндпоинты:
   - `GET /health` — проверка здоровья.
   - `GET /metrics/json` — JSON‑снимок метрик (CPU/RAM/Disk/Net).
   - `GET /metrics` — экспорт метрик для Prometheus.

Roadmap
- См. `ROADMAP.md` (RU) и `ROADMAP.en.md` (EN) — план на 2023 по кварталам.

Язык
- Private Usage: RU (`PRIVATE_USAGE.txt`) — локальный файл, игнорируется Git.
