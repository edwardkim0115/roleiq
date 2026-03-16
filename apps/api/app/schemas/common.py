from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class TimestampedRead(AppBaseModel):
    created_at: datetime

