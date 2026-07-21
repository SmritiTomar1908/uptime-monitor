from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class MonitorCreate(BaseModel):
    url: HttpUrl


class LatestCheck(BaseModel):
    status_code: int | None
    response_time_ms: float | None
    is_up: bool
    error: str | None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MonitorResponse(BaseModel):
    id: int
    url: str
    created_at: datetime
    is_active: bool
    latest_check: LatestCheck | None = None


class HealthCheckResponse(LatestCheck):
    id: int
    monitor_id: int
