from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .checker import check_monitor, run_all_checks
from .database import Base, SessionLocal, engine
from .models import HealthCheck, Monitor
from .schemas import HealthCheckResponse, MonitorCreate, MonitorResponse

scheduler = BackgroundScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler.add_job(
        run_all_checks,
        "interval",
        seconds=60,
        id="uptime-check-job",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Uptime Monitor API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_monitor(monitor: Monitor, db: Session) -> MonitorResponse:
    latest = db.scalar(
        select(HealthCheck)
        .where(HealthCheck.monitor_id == monitor.id)
        .order_by(desc(HealthCheck.checked_at))
        .limit(1)
    )
    return MonitorResponse(
        id=monitor.id,
        url=monitor.url,
        created_at=monitor.created_at,
        is_active=monitor.is_active,
        latest_check=latest,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/monitors", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
def create_monitor(payload: MonitorCreate, db: Session = Depends(get_db)):
    monitor = Monitor(url=str(payload.url))
    db.add(monitor)
    try:
        db.commit()
        db.refresh(monitor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="URL is already registered")

    check_monitor(monitor, db)
    return serialize_monitor(monitor, db)


@app.get("/api/monitors", response_model=list[MonitorResponse])
def list_monitors(db: Session = Depends(get_db)):
    monitors = db.scalars(select(Monitor).order_by(desc(Monitor.created_at))).all()
    return [serialize_monitor(monitor, db) for monitor in monitors]


@app.post("/api/monitors/{monitor_id}/check", response_model=HealthCheckResponse)
def check_now(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return check_monitor(monitor, db)


@app.get("/api/monitors/{monitor_id}/checks", response_model=list[HealthCheckResponse])
def check_history(monitor_id: int, limit: int = 20, db: Session = Depends(get_db)):
    monitor = db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    safe_limit = min(max(limit, 1), 100)
    return db.scalars(
        select(HealthCheck)
        .where(HealthCheck.monitor_id == monitor_id)
        .order_by(desc(HealthCheck.checked_at))
        .limit(safe_limit)
    ).all()


@app.delete("/api/monitors/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    db.delete(monitor)
    db.commit()
