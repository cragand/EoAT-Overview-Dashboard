# AI Context: EOAT Overview Dashboard

## Project Overview
Web-based fleet tracking dashboard for EOAT (End of Arm Tooling) devices. Aggregates data from multiple Asana projects into a unified view with table, kanban, and device detail pages.

## Application Name
- **Full Name**: EOAT Overview Dashboard
- **Repository**: EoAT-Overview-Dashboard

## Related Project
- **Emtech EoAT Workbench Wizard (EEWW)** — Separate PyQt5 desktop app for hands-on QC/maintenance workflows with camera integration. Lives in `../camera_qc_app/`. The EOAT devices tracked in this dashboard are the same hardware that EEWW performs QC and maintenance procedures on.

## Core Purpose
- Provide big-picture visibility into the entire EOAT fleet
- Track device status, location, assignment, and work history
- Replace manual weekly change-detection scripts with automated sync
- Enable multiple users to view fleet status via web browser

## Technology Stack
- **Backend**: Python 3.7+, Flask, Flask-SQLAlchemy
- **Database**: SQLite (file: `eoat_tracker.db`, gitignored)
- **Frontend**: Vanilla HTML/CSS/JS, dark theme
- **Data Source**: Asana CSV exports (API integration planned via OAuth 2.0 or PAT)
- **No frontend framework** — plain Jinja2 templates with minimal JS for search/filter/sort

## Data Sources (Asana)

### EOAT Tracker Portfolio
- Each EOAT unit is its own Asana project within a portfolio
- Custom fields: serial number, version ID, status, assignment, current location, build location, allocation, workcell ID, customer, POC, planned location/workcell
- Component serial numbers: base, static jaw, mobile jaw, electrical enclosure, bin manipulator
- Additional: tracker tags (change history), e-traveler links, RMTO SN
- ~45 devices currently (EoAT6, EoAT7, EoAT8, EoAT9 variants)

### All EOAT Work Project
- Tasks represent work events: repairs, QA inspections, installations, maintenance, EOL tests
- Tasks linked to devices via `EoAT Serial #` custom field
- Parent-child task hierarchy: e.g. "EOAT Repair - 7026" parent with subtasks "Duckbilling repair", "Pre-shipment QA"
- ~2000 events, submitted via Vulcan Subsystem RMA form
- Many subtasks lack serial number field — inherit context from parent task
- Key fields: task name, section/column, assignee, dates, site, workcell, work category, subassembly, task status

### CSV Column Name Quirks
- Asana exports use **unicode bold/styled characters** in some column headers (e.g. `𝗘𝗼𝗔𝗧 𝗦𝗲𝗿𝗶𝗮𝗹 #`)
- Import code uses `unicodedata.normalize('NFKC', ...)` to match columns reliably
- Some columns have superscript annotations like `⁽ᵛˢ⁾` or `⁽ᴬᴿ⁾`

## Application Architecture

### Flask App (`app.py`)
- `create_app()` factory pattern
- Routes: `/` (table), `/kanban`, `/device/<serial>`, `/api/devices`
- Auto-imports CSVs from `data/` on startup if newer than last sync
- SQLite database created automatically on first run

### Database Models (`models.py`)
- **EoatDevice**: One row per EOAT unit. 30+ fields covering identity, status, location, components, links, metadata
- **EoatEvent**: One row per work task. Links to device by serial_number and device_id FK
- **SyncLog**: Tracks import timestamps and change counts per source

### CSV Import (`import_csv.py`, `auto_import.py`)
- `import_portfolio_csv()`: Imports/updates devices from portfolio export. Upserts by serial_number.
- `import_events_csv()`: Imports events from task export. Deduplicates by asana_task_gid.
- `auto_import()`: Called on app startup. Compares CSV file modified time against last SyncLog timestamp. Skips if unchanged.
- Column matching uses fuzzy unicode-normalized search via `_find_col()`

### Asana API Integration (Prepared, Not Active)
- **auth.py**: OAuth 2.0 flow — terminal-based code exchange (no web server needed for auth)
- **asana_client.py**: Authenticated GET wrapper for Asana REST API
- **explore_workspace.py**: Maps workspace structure (portfolios, projects, custom fields)
- **config.py**: Source configuration with field mappings for EOAT Tracker portfolio and All EOAT Work project
- Blocked on: OAuth app admin approval or PAT from team lead
- OAuth Client ID: 1214238330439160 (registered as "EOAT Overview Dashboard")

### Frontend
- **Dark theme** with CSS custom properties (Emtech green accent #77C25E)
- **Table view**: Sortable columns, text search, dropdown filters (status, type, assignment)
- **Kanban board**: Cards grouped by assignment/status with location and workcell info
- **Device detail**: Info grid, component serials section, change history tags, work event timeline
- **JS**: Vanilla — client-side filtering/sorting, no build step

## EOAT Device Types
- **EoAT6**: Older generation, some marked Obsolete
- **EoAT7**: Current primary fleet (~30 units), version 07.01.03
- **EoAT8**: Variant (~4 units), version 08.00.00
- **EoAT9**: Variant (~2 units), version 09.00.00

## EOAT Statuses
- **Complete**: Built and operational (most common)
- **Obsolete**: Retired/decommissioned

## EOAT Assignments
- **Deployment**: Actively installed at a site/workcell
- **Spare**: Available as backup

## Key Locations
- **GEG1-Beta**: Primary deployment site
- **SEA90**: Build/lab location (EoAT7 Lab, Beta 1:1, Beta 1:3, Static Cells)
- **SEA89**: Reliability testing
- **BOS27**: Build location for newer units
- **OWD9-Beta**: Deployment site
- **BFI1**: Deployment site
- **MTAC**: Deployment site

## Common Work Event Types
- **R-EOAT Replacement**: Full EOAT swap at a site (submitted via RMA form)
- **EOAT Repair**: Repair tracking with subtasks (duckbilling repair, belt replacement, etc.)
- **Pre-shipment QA**: Quality check before shipping repaired unit
- **EOL Test**: End-of-line testing
- **STO Retrofit**: Safety retrofit work
- **Integration Testing**: Testing after installation

## Development Guidelines

### Adding New Fields
1. Add column to `EoatDevice` or `EoatEvent` in `models.py`
2. Add mapping in `import_csv.py` (`_find_col` call + assignment)
3. Delete `eoat_tracker.db` to recreate schema (or use migrations)
4. Update templates to display new field

### Updating Dashboard Views
- Templates in `templates/` use Jinja2
- Styles in `static/style.css` — CSS custom properties for theming
- Client-side logic in `static/dashboard.js`

### Testing Imports
```bash
rm -f eoat_tracker.db
python import_csv.py portfolio data/EOAT_Tracker.csv
python import_csv.py events data/All_EOAT_Work.csv
```

### Running the App
- Windows: `run_dashboard.bat` (handles venv, deps, startup)
- Linux: `source venv/bin/activate && python app.py`
- Opens on http://localhost:5000

## Important Design Decisions
- **SQLite for simplicity** — Single file DB, no server needed. Upgrade to PostgreSQL when deploying to Harmony for multi-user.
- **CSV import as primary data path** — Until Asana API access is approved. Auto-import on startup minimizes manual steps.
- **No frontend framework** — Keeps it simple, fast, zero build step. Vanilla JS handles search/filter/sort.
- **Unicode normalization for Asana headers** — Asana exports styled unicode characters in column names. NFKC normalization handles this transparently.
- **Serial number as linking key** — Devices and events are connected by serial number across both Asana sources.

## Planned Enhancements
- Asana API live sync (PAT or OAuth) with configurable interval
- Cron job for automated sync every 30 minutes
- Improved event-to-device linking for subtasks (inherit serial from parent task)
- Deployment to Amazon Harmony cloud console for multi-user access
- User roles/permissions (future)
