# EOAT Overview Dashboard

Real-time fleet tracking dashboard for EOAT (End of Arm Tooling) devices, aggregating data from multiple Asana projects into a unified web interface.

## Quick Start (Windows)

1. Double-click `run_dashboard.bat`
2. Open http://localhost:5000 in your browser
3. First run automatically sets up the environment (~1 minute)

## Quick Start (Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000.

## Data Sources

The dashboard pulls EOAT data from two Asana sources:

- **EOAT Tracker** portfolio — Each EOAT unit is its own Asana project with custom fields (serial number, version, status, location, assignment, workcell, component serials, etc.)
- **All EOAT Work** project — Tasks representing work events (repairs, QA, installations, maintenance) tagged to specific EOATs by serial number

### Loading Data via CSV Export

1. Export both sources as CSV from Asana
2. Place them in the `data/` folder:
   - Portfolio export → filename containing "tracker" or "portfolio"
   - Work/events export → filename containing "work", "event", or "task"
3. Start the app — it auto-imports CSVs that are newer than the last import
4. To refresh data, overwrite the CSVs with new exports and restart

### Loading Data via Asana API (Future)

Once OAuth app approval or a PAT is available, the dashboard will sync directly from Asana on a configurable schedule, replacing the CSV workflow entirely.

## Dashboard Views

### Table View (`/`)
- Sortable, filterable table of all EOAT devices
- Filter by status (Complete, Obsolete), EOAT type (EoAT6/7/8/9), and assignment (Deployment, Spare)
- Full-text search across all fields
- Click any device to view its detail page

### Kanban Board (`/kanban`)
- Devices grouped by assignment/status in card columns
- Each card shows location, workcell, allocation, and assignment
- Click cards to navigate to device detail

### Device Detail (`/device/<serial>`)
- Full device information: serial, version, type, status, location, workcell, allocation, customer, owner, POC
- Component serial numbers (base, static jaw, mobile jaw, electrical enclosure, bin manipulator)
- Links to Asana project and E-Traveler documents
- Change history tags
- Complete work history timeline with event details

### JSON API (`/api/devices`)
- Returns all devices as JSON for programmatic access

## Project Structure

```
eoat_tracker/
├── app.py                 # Flask application and routes
├── models.py              # SQLAlchemy database models
├── db.py                  # Database setup
├── config.py              # Configuration (Asana sources, sync settings)
├── import_csv.py          # CSV import for portfolio and events
├── auto_import.py         # Auto-import CSVs on startup if newer
├── auth.py                # Asana OAuth 2.0 authentication flow
├── asana_client.py        # Asana API wrapper
├── explore_workspace.py   # Asana workspace structure explorer
├── seed.py                # Mock data seeder (development)
├── requirements.txt       # Python dependencies
├── run_dashboard.bat      # Windows one-click launcher
├── .env                   # Asana credentials (gitignored)
├── .gitignore
├── templates/
│   ├── base.html          # Layout with navigation
│   ├── dashboard.html     # Table view
│   ├── kanban.html        # Kanban board
│   └── device_detail.html # Device detail + timeline
├── static/
│   ├── style.css          # Dark theme styling
│   └── dashboard.js       # Client-side search/filter/sort
└── data/                  # CSV exports from Asana (gitignored in future)
```

## Database Schema

### eoat_devices
Core device record — one row per EOAT unit.

| Field | Description | Example |
|---|---|---|
| serial_number | Unique identifier | 7041 |
| name | Asana project name | EoAT7-041 |
| eoat_type | Device family | EoAT7 |
| version_id | Firmware/hardware version | 07.01.03 |
| status | Operational status | Complete, Obsolete |
| assignment | Deployment or Spare | Deployment |
| current_location | Physical location | GEG1-Beta |
| build_location | Where it was built | BOS27 |
| allocation | Project/site allocation | GEG1-Beta |
| workcell_id | Installed workcell | 4447 WC2 |
| customer | Responsible contact | email address |
| Component SNs | Base, Static Jaw, Mobile Jaw, Electrical Enclosure, Bin Manipulator | Part serial numbers |

### eoat_events
Work history — one row per task/event from "All EOAT Work".

| Field | Description |
|---|---|
| serial_number | Links to device |
| event_name | Task name |
| event_type | Work category (Repairs, etc.) |
| section | Asana section (Repair Depot, etc.) |
| performed_by | Technician name and email |
| date / completed_at | When created and completed |
| site / workcell_id | Where the work occurred |

## Technology Stack

- **Backend:** Python 3.7+, Flask, SQLAlchemy
- **Database:** SQLite (upgradeable to PostgreSQL for multi-user)
- **Frontend:** HTML/CSS/JS (no framework, dark theme)
- **Data source:** Asana CSV exports (API integration planned)

## Deployment Target

Currently runs locally. Planned deployment to Amazon Harmony cloud console for multi-user access.

## License

Internal use only — Emtech
