from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class AutomationRecord(Base):
    __tablename__ = "automations_sql"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    trigger_type: Mapped[str] = mapped_column(String(120))
    action_type: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(50), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
