from sqlalchemy.orm import Session

from models.automation_sql import AutomationRecord
from models.schemas import SaveAutomationRequest


class AutomationSQLService:
    @staticmethod
    def save(db: Session, user_id: str, payload: SaveAutomationRequest) -> AutomationRecord:
        record = AutomationRecord(
            user_id=user_id,
            prompt=payload.prompt,
            trigger_type=payload.trigger_type,
            action_type=payload.action_type,
            status=payload.status,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
