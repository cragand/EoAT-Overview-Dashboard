"""Configuration for Asana sources and app settings."""
import os
from dotenv import load_dotenv

load_dotenv()

# Asana OAuth
ASANA_CLIENT_ID = os.getenv("ASANA_CLIENT_ID")
ASANA_CLIENT_SECRET = os.getenv("ASANA_CLIENT_SECRET")
ASANA_REDIRECT_URI = os.getenv("ASANA_REDIRECT_URI")

# Asana sources — fill in GIDs once API access is approved
ASANA_SOURCES = {
    "eoat_tracker_portfolio": {
        "type": "portfolio",
        "gid": None,  # To be filled
        "name": "EOAT Tracker",
        "description": "Portfolio where each project is an individual EOAT unit",
        "field_mapping": {
            "Customer": "customer",
            "EOAT Version ID": "version_id",
            "EOAT Status": "status",
            "Current Location": "current_location",
            "Workcell ID": "workcell_id",
            "Allocation": "allocation",
            "Assignment": "assignment",
            "Build Location": "build_location",
            "EOAT Serial Number": "serial_number",
        },
    },
    "all_eoat_work": {
        "type": "project",
        "gid": None,  # To be filled
        "name": "All EOAT Work",
        "description": "Project with tasks representing work events on EOATs",
        "serial_field": "EOAT Serial Number",
    },
}

# Sync settings
SYNC_INTERVAL_MINUTES = 5

# Database
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "eoat_tracker.db")
