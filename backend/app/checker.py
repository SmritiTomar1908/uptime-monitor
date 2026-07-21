import time

import httpx
from sqlalchemy import select

from .database import SessionLocal
from .models import HealthCheck, Monitor

TIMEOUT_SECONDS = 10.0


def check_monitor(monitor: Monitor, db) -> HealthCheck:
    start = time.perf_counter()
    status_code = None
    error = None
    is_up = False

    try:
        with httpx.Client(
            timeout=TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": "Simple-Uptime-Monitor/1.0"},
        ) as client:
            response = client.get(monitor.url)
            status_code = response.status_code
            is_up = 200 <= response.status_code < 400
    except httpx.HTTPError as exc:
        error = str(exc)[:500]

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    check = HealthCheck(
        monitor_id=monitor.id,
        status_code=status_code,
        response_time_ms=elapsed_ms,
        is_up=is_up,
        error=error,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


def run_all_checks() -> None:
    db = SessionLocal()
    try:
        monitors = db.scalars(select(Monitor).where(Monitor.is_active.is_(True))).all()
        for monitor in monitors:
            check_monitor(monitor, db)
    finally:
        db.close()
