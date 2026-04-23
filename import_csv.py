"""Import EOAT data from Asana CSV exports."""
import csv
import io
import re
import sys
from datetime import datetime, timezone
from models import EoatDevice, EoatEvent, SyncLog
from db import db

# Normalize unicode-styled column names to plain ASCII keys
def _normalize_header(header):
    """Strip unicode bold/styled chars and superscripts from column names."""
    # Map bold unicode ranges to ASCII
    replacements = {}
    for styled, plain in [
        ('\U0001d5d7', 'D'), ('\U0001d5d8', 'E'), ('\U0001d5d9', 'F'),
    ]:
        replacements[styled] = plain
    # Simpler approach: just use the raw header as-is for matching
    return header.strip()


def _parse_date(val):
    if not val or not val.strip():
        return None
    val = val.strip()
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(val, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _extract_eoat_type(name):
    """Extract EOAT type from project name like 'EoAT7-041' -> 'EoAT7'."""
    m = re.match(r'(EoAT\d+)', name or '', re.IGNORECASE)
    return m.group(1) if m else None


def _find_col(headers, *candidates):
    """Find a column by trying multiple name variants."""
    for c in candidates:
        for h in headers:
            if c.lower() in h.lower():
                return h
    return None


def import_portfolio_csv(filepath):
    """Import EOAT Tracker portfolio CSV (device-level data)."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        # Find columns (handles unicode-styled names)
        col_name = _find_col(headers, 'NAME')
        col_serial = _find_col(headers, 'Serial #', 'Serial')
        col_version = _find_col(headers, 'EOAT Version ID')
        col_status = _find_col(headers, 'EOAT Status')
        col_assignment = _find_col(headers, 'Assignment')
        col_location = _find_col(headers, 'Current Location')
        col_build = _find_col(headers, 'Build Location')
        col_allocation = _find_col(headers, 'Allocation')
        col_workcell = _find_col(headers, 'Workcell ID', 'Workcell')
        col_customer = _find_col(headers, 'Customer')
        col_project = _find_col(headers, 'Project', 'Projet')
        col_poc = _find_col(headers, 'POC')
        col_owner = _find_col(headers, 'OWNER')
        col_url = _find_col(headers, 'URL')
        col_planned_loc = _find_col(headers, 'Planned Location')
        col_planned_wc = _find_col(headers, 'Planned Workcell')
        col_tracker_tag = _find_col(headers, 'Tracker Tag')
        col_e_traveler = _find_col(headers, 'Electronic Serial')
        col_rmto = _find_col(headers, 'RMTO')
        col_base = _find_col(headers, 'Base Serial')
        col_static_jaw = _find_col(headers, 'Static Jaw')
        col_mobile_jaw = _find_col(headers, 'Mobile Jaw')
        col_elec_enc = _find_col(headers, 'Electrical Enclosure')
        col_bin_manip = _find_col(headers, 'Bin Manipulator')

        imported = 0
        updated = 0
        skipped = 0

        for row in reader:
            name = (row.get(col_name) or '').strip()
            # Skip non-device rows (like "All EOAT Work")
            if not name or not re.match(r'EoAT', name, re.IGNORECASE):
                skipped += 1
                continue

            serial = (row.get(col_serial) or '').strip()
            if not serial:
                skipped += 1
                continue

            device = EoatDevice.query.filter_by(serial_number=serial).first()
            is_new = device is None
            if is_new:
                device = EoatDevice(serial_number=serial)

            device.name = name
            device.eoat_type = _extract_eoat_type(name)
            device.version_id = (row.get(col_version) or '').strip() or None
            device.status = (row.get(col_status) or '').strip() or None
            device.assignment = (row.get(col_assignment) or '').strip() or None
            device.current_location = (row.get(col_location) or '').strip() or None
            device.build_location = (row.get(col_build) or '').strip() or None
            device.allocation = (row.get(col_allocation) or '').strip() or None
            device.workcell_id = (row.get(col_workcell) or '').strip() or None
            device.customer = (row.get(col_customer) or '').strip() or None
            device.project_type = (row.get(col_project) or '').strip() or None
            device.poc = (row.get(col_poc) or '').strip() or None
            device.owner = (row.get(col_owner) or '').strip() or None
            device.asana_url = (row.get(col_url) or '').strip() or None
            device.planned_location = (row.get(col_planned_loc) or '').strip() or None
            device.planned_workcell = (row.get(col_planned_wc) or '').strip() or None
            device.tracker_tag = (row.get(col_tracker_tag) or '').strip() or None
            device.e_traveler_link = (row.get(col_e_traveler) or '').strip() or None
            device.rmto_sn = (row.get(col_rmto) or '').strip() or None
            device.base_sn = (row.get(col_base) or '').strip() or None
            device.static_jaw_sn = (row.get(col_static_jaw) or '').strip() or None
            device.mobile_jaw_sn = (row.get(col_mobile_jaw) or '').strip() or None
            device.electrical_enclosure_sn = (row.get(col_elec_enc) or '').strip() or None
            device.bin_manipulator_sn = (row.get(col_bin_manip) or '').strip() or None
            device.last_synced = datetime.now(timezone.utc)

            if is_new:
                db.session.add(device)
                imported += 1
            else:
                updated += 1

        # Log the sync
        log = SyncLog(
            source="portfolio_csv",
            changes_detected=imported + updated,
            details=f"Imported {imported} new, updated {updated}, skipped {skipped}",
        )
        db.session.add(log)
        db.session.commit()

    print(f"Portfolio import: {imported} new devices, {updated} updated, {skipped} skipped")
    return imported, updated


def import_events_csv(filepath):
    """Import All EOAT Work CSV (event/task data)."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        col_task_id = _find_col(headers, 'Task ID')
        col_created = _find_col(headers, 'Created At')
        col_completed = _find_col(headers, 'Completed At')
        col_name = _find_col(headers, 'Name')
        col_section = _find_col(headers, 'Section/Column')
        col_assignee = _find_col(headers, 'Assignee')
        col_email = _find_col(headers, 'Assignee Email')
        col_due = _find_col(headers, 'Due Date')
        col_notes = _find_col(headers, 'Notes')
        col_projects = _find_col(headers, 'Projects')
        col_parent = _find_col(headers, 'Parent task')
        col_serial = _find_col(headers, 'Serial #', 'Serial')
        col_site = _find_col(headers, 'Site')
        col_workcell = _find_col(headers, 'Workcell')
        col_work_cat = _find_col(headers, 'Work Category')
        col_subassembly = _find_col(headers, 'Subassembly')
        col_task_status = _find_col(headers, 'Task Status')

        imported = 0
        skipped = 0

        for row in reader:
            task_gid = (row.get(col_task_id) or '').strip()
            serial = (row.get(col_serial) or '').strip()
            task_name = (row.get(col_name) or '').strip()

            if not task_name:
                skipped += 1
                continue

            # Skip if already imported
            if task_gid:
                existing = EoatEvent.query.filter_by(asana_task_gid=task_gid).first()
                if existing:
                    skipped += 1
                    continue

            # Try to link to a device
            device = None
            if serial:
                device = EoatDevice.query.filter_by(serial_number=serial).first()

            # Extract source projects
            projects_str = (row.get(col_projects) or '').strip()

            event = EoatEvent(
                device_id=device.id if device else None,
                serial_number=serial or '',
                event_type=(row.get(col_work_cat) or '').strip() or None,
                event_name=task_name,
                section=(row.get(col_section) or '').strip() or None,
                description=(row.get(col_notes) or '').strip()[:2000] if row.get(col_notes) else None,
                performed_by=(row.get(col_assignee) or '').strip() or None,
                performed_by_email=(row.get(col_email) or '').strip() or None,
                date=_parse_date(row.get(col_created)),
                completed_at=_parse_date(row.get(col_completed)),
                due_date=_parse_date(row.get(col_due)),
                site=(row.get(col_site) or '').strip() or None,
                workcell_id=(row.get(col_workcell) or '').strip() or None,
                subassembly=(row.get(col_subassembly) or '').strip() or None,
                task_status=(row.get(col_task_status) or '').strip() or None,
                parent_task=(row.get(col_parent) or '').strip() or None,
                asana_task_gid=task_gid or None,
                source_project=projects_str[:256] if projects_str else None,
            )
            db.session.add(event)
            imported += 1

            # Batch commit every 500 rows
            if imported % 500 == 0:
                db.session.flush()

        log = SyncLog(
            source="events_csv",
            changes_detected=imported,
            details=f"Imported {imported} events, skipped {skipped}",
        )
        db.session.add(log)
        db.session.commit()

    print(f"Events import: {imported} events imported, {skipped} skipped")
    return imported


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        if len(sys.argv) < 3:
            print("Usage: python import_csv.py <portfolio|events> <filepath>")
            print("  python import_csv.py portfolio data/eoat_tracker_portfolio.csv")
            print("  python import_csv.py events data/all_eoat_work.csv")
            sys.exit(1)

        mode = sys.argv[1]
        filepath = sys.argv[2]

        if mode == 'portfolio':
            import_portfolio_csv(filepath)
        elif mode == 'events':
            import_events_csv(filepath)
        else:
            print(f"Unknown mode: {mode}. Use 'portfolio' or 'events'.")
            sys.exit(1)
