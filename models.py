"""SQLAlchemy models for EOAT tracking."""
from datetime import datetime, timezone
from db import db


class EoatDevice(db.Model):
    __tablename__ = "eoat_devices"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    version_id = db.Column(db.String(32))
    status = db.Column(db.String(64))
    customer = db.Column(db.String(128))
    current_location = db.Column(db.String(128))
    workcell_id = db.Column(db.String(64))
    allocation = db.Column(db.String(128))
    assignment = db.Column(db.String(64))
    build_location = db.Column(db.String(128))
    asana_project_gid = db.Column(db.String(64))
    last_synced = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    events = db.relationship("EoatEvent", backref="device", lazy="dynamic",
                             order_by="EoatEvent.date.desc()")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class EoatEvent(db.Model):
    __tablename__ = "eoat_events"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("eoat_devices.id"), nullable=False, index=True)
    serial_number = db.Column(db.String(64), nullable=False, index=True)
    event_type = db.Column(db.String(64))
    description = db.Column(db.Text)
    performed_by = db.Column(db.String(128))
    date = db.Column(db.DateTime)
    asana_task_gid = db.Column(db.String(64))
    source_project = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class SyncLog(db.Model):
    __tablename__ = "sync_log"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    source = db.Column(db.String(128))
    changes_detected = db.Column(db.Integer, default=0)
    details = db.Column(db.Text)
