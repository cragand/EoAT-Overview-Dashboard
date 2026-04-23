"""Seed database with mock data (only if no real data exists)."""
from models import EoatDevice
from db import db


def seed_mock_data():
    """Skip seeding — use import_csv.py with real Asana exports instead."""
    if EoatDevice.query.first():
        return
    print("No devices in database. Import data with:")
    print("  python import_csv.py portfolio data/eoat_tracker_portfolio.csv")
    print("  python import_csv.py events data/all_eoat_work.csv")
