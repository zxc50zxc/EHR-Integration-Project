from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal
from backend.database.models import AuditLog


def log_audit(
    user_id: int | None,
    action: str,
    resource_type: str | None = None,
    resource_id: int | None = None,
    details: str | None = None,
    ip_address: str | None = None,
    db: Session | None = None,
) -> AuditLog | None:
    owns_session = db is None
    db = db or SessionLocal()
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        timestamp=datetime.now(UTC),
    )
    try:
        db.add(entry)
        db.flush()
        if owns_session:
            db.commit()
        return entry
    except Exception:
        if owns_session:
            db.rollback()
        return None
    finally:
        if owns_session:
            db.close()


def write_audit_log(
    db: Session,
    *,
    action,
    resource_type: str,
    resource_id: int | str | None = None,
    user=None,
    ip_address: str | None = None,
    details: dict | str | None = None,
) -> AuditLog | None:
    return log_audit(
        user_id=getattr(user, "id", None),
        action=getattr(action, "value", str(action)),
        resource_type=resource_type,
        resource_id=int(resource_id) if isinstance(resource_id, str) and resource_id.isdigit() else resource_id,
        details=str(details) if details is not None else None,
        ip_address=ip_address,
        db=db,
    )
