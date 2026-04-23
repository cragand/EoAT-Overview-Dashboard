"""Auto-import CSVs from data/ if they're newer than last sync."""
import os
from datetime import datetime, timezone
from models import SyncLog
from db import db

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _csv_modified_time(filepath):
    if not os.path.exists(filepath):
        return None
    return datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)


def _last_sync_time(source):
    log = SyncLog.query.filter_by(source=source).order_by(SyncLog.timestamp.desc()).first()
    return log.timestamp.replace(tzinfo=timezone.utc) if log and log.timestamp else None


def auto_import():
    """Check data/ for CSVs newer than last import and re-import if needed."""
    from import_csv import import_portfolio_csv, import_events_csv

    portfolio_file = None
    events_file = None

    if not os.path.isdir(DATA_DIR):
        return

    for f in os.listdir(DATA_DIR):
        fl = f.lower()
        if fl.endswith('.csv'):
            if 'tracker' in fl or 'portfolio' in fl:
                portfolio_file = os.path.join(DATA_DIR, f)
            elif 'work' in fl or 'event' in fl or 'task' in fl:
                events_file = os.path.join(DATA_DIR, f)

    if portfolio_file:
        csv_time = _csv_modified_time(portfolio_file)
        last_sync = _last_sync_time("portfolio_csv")
        if csv_time and (last_sync is None or csv_time > last_sync):
            print(f"Auto-importing portfolio: {os.path.basename(portfolio_file)}")
            import_portfolio_csv(portfolio_file)

    if events_file:
        csv_time = _csv_modified_time(events_file)
        last_sync = _last_sync_time("events_csv")
        if csv_time and (last_sync is None or csv_time > last_sync):
            print(f"Auto-importing events: {os.path.basename(events_file)}")
            import_events_csv(events_file)
