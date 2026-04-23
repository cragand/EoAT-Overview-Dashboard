"""SQLAlchemy models for EOAT tracking."""
from datetime import datetime, timezone
from db import db


class EoatDevice(db.Model):
    __tablename__ = "eoat_devices"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128))  # e.g. "EoAT7-041"
    version_id = db.Column(db.String(32))  # e.g. "07.01.03"
    eoat_type = db.Column(db.String(32))  # e.g. "EoAT7", "EoAT8", "EoAT9"
    status = db.Column(db.String(64))  # "Complete", "Obsolete"
    assignment = db.Column(db.String(64))  # "Deployment", "Spare"
    current_location = db.Column(db.String(128))
    build_location = db.Column(db.String(128))
    allocation = db.Column(db.String(128))
    workcell_id = db.Column(db.String(64))
    customer = db.Column(db.String(128))
    project_type = db.Column(db.String(64))  # from 𝗣𝗿𝗼𝗷𝗲𝗰𝘁 field
    poc = db.Column(db.String(128))  # point of contact
    owner = db.Column(db.String(128))  # Asana project owner
    planned_location = db.Column(db.String(128))
    planned_workcell = db.Column(db.String(64))
    tracker_tag = db.Column(db.Text)  # change history tags
    e_traveler_link = db.Column(db.String(512))
    rmto_sn = db.Column(db.String(128))
    asana_url = db.Column(db.String(512))
    # Component serial numbers
    base_sn = db.Column(db.String(128))
    static_jaw_sn = db.Column(db.String(128))
    mobile_jaw_sn = db.Column(db.String(128))
    electrical_enclosure_sn = db.Column(db.String(128))
    bin_manipulator_sn = db.Column(db.String(128))
    # Metadata
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
    device_id = db.Column(db.Integer, db.ForeignKey("eoat_devices.id"), index=True)
    serial_number = db.Column(db.String(64), nullable=False, index=True)
    event_type = db.Column(db.String(64))  # Work Category
    event_name = db.Column(db.String(256))  # Task name
    section = db.Column(db.String(128))  # Section/Column from Asana
    description = db.Column(db.Text)
    performed_by = db.Column(db.String(128))
    performed_by_email = db.Column(db.String(128))
    date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    site = db.Column(db.String(64))
    workcell_id = db.Column(db.String(64))
    subassembly = db.Column(db.String(128))
    task_status = db.Column(db.String(64))
    parent_task = db.Column(db.String(256))
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
