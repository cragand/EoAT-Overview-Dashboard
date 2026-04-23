"""Seed database with realistic mock EOAT data."""
from datetime import datetime, timedelta, timezone
import random
from models import EoatDevice, EoatEvent
from db import db

VERSIONS = ["EoAT5", "EoAT6", "EoAT7", "EoAT7", "EoAT7"]  # weighted toward v7
STATUSES = ["Deployed", "In Storage", "Under Maintenance", "QC In Progress",
            "Ready for Deployment", "Decommissioned"]
LOCATIONS = ["Building 40", "Building 18", "Building 12", "Lab 3A", "Lab 7B",
             "Warehouse C", "Customer Site - Detroit", "Customer Site - Austin"]
WORKCELLS = ["WC-101", "WC-102", "WC-203", "WC-204", "WC-305", "WC-410", None, None]
ALLOCATIONS = ["Project Alpha", "Project Beta", "Project Gamma", "Line 4 Expansion",
               "Customer Demo", "R&D Testing", None]
ASSIGNMENTS = ["Deployment", "Spare", "Deployment", "Deployment", "Spare"]
BUILD_LOCATIONS = ["Building 40", "Building 18", "Building 12"]
CUSTOMERS = ["Line 4 - Detroit", "Line 2 - Austin", "Lab Team A", "Lab Team B",
             "Field Ops", "R&D Group", None]
EVENT_TYPES = ["Build Complete", "QC Inspection", "Final QA", "Installation",
               "Maintenance", "Belt Replacement", "Calibration", "Relocation",
               "Storage", "Deployment", "Decommission"]
TECHNICIANS = ["J. Smith", "M. Chen", "A. Rodriguez", "K. Patel", "T. Williams"]


def seed_mock_data():
    """Populate DB with realistic mock EOAT data."""
    if EoatDevice.query.first():
        return  # Already seeded

    now = datetime.now(timezone.utc)
    devices = []

    for i in range(1, 21):
        serial = f"EOAT-{i:03d}"
        version = random.choice(VERSIONS)
        status = random.choice(STATUSES)
        assignment = random.choice(ASSIGNMENTS)

        # Deployed units get location/workcell; stored units don't
        if status == "Deployed":
            location = random.choice([l for l in LOCATIONS if "Customer" in l or "Building" in l])
            workcell = random.choice([w for w in WORKCELLS if w])
            customer = random.choice([c for c in CUSTOMERS if c])
        elif status == "In Storage":
            location = random.choice(["Warehouse C", "Building 40"])
            workcell = None
            customer = None
            assignment = "Spare"
        else:
            location = random.choice(LOCATIONS[:3])
            workcell = None
            customer = None

        device = EoatDevice(
            serial_number=serial,
            version_id=version,
            status=status,
            customer=customer,
            current_location=location,
            workcell_id=workcell,
            allocation=random.choice(ALLOCATIONS) if status == "Deployed" else None,
            assignment=assignment,
            build_location=random.choice(BUILD_LOCATIONS),
            last_synced=now,
        )
        db.session.add(device)
        db.session.flush()
        devices.append(device)

        # Generate event history for each device
        build_date = now - timedelta(days=random.randint(60, 400))
        event_date = build_date
        events_for_device = ["Build Complete", "QC Inspection", "Final QA"]

        if status == "Deployed":
            events_for_device += ["Installation", "Deployment"]
            if random.random() > 0.5:
                events_for_device.append("Maintenance")
        elif status == "Under Maintenance":
            events_for_device += ["Installation", "Deployment", "Maintenance"]
        elif status == "Decommissioned":
            events_for_device += ["Installation", "Deployment", "Decommission"]

        for evt_type in events_for_device:
            event_date += timedelta(days=random.randint(1, 30))
            event = EoatEvent(
                device_id=device.id,
                serial_number=serial,
                event_type=evt_type,
                description=f"{evt_type} performed on {serial}",
                performed_by=random.choice(TECHNICIANS),
                date=event_date,
                source_project="All EOAT Work",
            )
            db.session.add(event)

    db.session.commit()
    print(f"Seeded {len(devices)} mock EOAT devices with event histories.")
