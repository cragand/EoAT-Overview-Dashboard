"""EOAT Tracker Dashboard — Flask application."""
from flask import Flask, render_template, jsonify, request
from config import DATABASE_PATH
from db import db
from models import EoatDevice, EoatEvent


def _template(name):
    """Return embed variant of template if ?embed=1."""
    if request.args.get('embed') == '1':
        return name.replace('.html', '_embed.html')
    return name


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        from auto_import import auto_import
        auto_import()

    @app.route("/")
    def home():
        devices = EoatDevice.query.all()
        events = EoatEvent.query.all()
        status_counts = {}
        assignment_counts = {}
        for d in devices:
            if d.status:
                status_counts[d.status] = status_counts.get(d.status, 0) + 1
            if d.assignment:
                assignment_counts[d.assignment] = assignment_counts.get(d.assignment, 0) + 1
        devices_with_events = len(set(
            e.serial_number for e in events if e.serial_number and e.device_id
        ))
        from models import SyncLog
        last_log = SyncLog.query.order_by(SyncLog.timestamp.desc()).first()
        last_sync = last_log.timestamp.strftime("%Y-%m-%d %H:%M") if last_log else "Never"
        return render_template("home.html",
                               device_count=len(devices),
                               event_count=len(events),
                               status_counts=status_counts,
                               assignment_counts=assignment_counts,
                               devices_with_events=devices_with_events,
                               last_sync=last_sync)

    @app.route("/dashboard")
    def dashboard():
        devices = EoatDevice.query.order_by(EoatDevice.name).all()
        status_counts = {}
        eoat_types = set()
        assignments = set()
        for d in devices:
            if d.status:
                status_counts[d.status] = status_counts.get(d.status, 0) + 1
            if d.eoat_type:
                eoat_types.add(d.eoat_type)
            if d.assignment:
                assignments.add(d.assignment)
        return render_template(_template("dashboard.html"), devices=devices,
                               status_counts=status_counts,
                               eoat_types=sorted(eoat_types),
                               assignments=sorted(assignments))

    @app.route("/kanban")
    def kanban():
        devices = EoatDevice.query.order_by(EoatDevice.name).all()
        columns = {}
        for d in devices:
            col = d.assignment or d.status or "Unknown"
            columns.setdefault(col, []).append(d)
        return render_template(_template("kanban.html"), columns=columns)

    @app.route("/device/<serial_number>")
    def device_detail(serial_number):
        device = EoatDevice.query.filter_by(serial_number=serial_number).first_or_404()
        events = EoatEvent.query.filter_by(serial_number=serial_number)\
            .order_by(EoatEvent.date.desc()).all()
        return render_template("device_detail.html", device=device, events=events)

    @app.route("/timeline")
    def timeline():
        devices = EoatDevice.query.order_by(EoatDevice.name).all()
        eoat_types = sorted(set(d.eoat_type for d in devices if d.eoat_type))
        assignments = sorted(set(d.assignment for d in devices if d.assignment))

        timeline_data = []
        for d in devices:
            events = EoatEvent.query.filter_by(serial_number=d.serial_number)\
                .order_by(EoatEvent.date.asc()).all()

            evt_list = []
            for e in events:
                if not e.date:
                    continue
                evt_list.append({
                    "date": e.date.strftime("%Y-%m-%d"),
                    "name": e.event_name or e.event_type or "Event",
                    "type": e.event_type,
                    "performed_by": e.performed_by,
                    "completed": e.completed_at is not None,
                    "description": (e.description or "")[:300],
                    "task_gid": e.asana_task_gid,
                    "section": e.section,
                    "site": e.site,
                    "workcell": e.workcell_id,
                })

            # Infer assignment periods from events
            periods = []
            current_period = None
            for e in events:
                if not e.date:
                    continue
                etype = (e.event_type or "").lower()
                ename = (e.event_name or "").lower()

                if "repair" in etype or "repair" in ename:
                    period_type = "Repairs"
                elif "install" in ename or "deployment" in ename:
                    period_type = "Deployment"
                elif "qa" in ename or "qc" in ename or "test" in ename:
                    period_type = "QA/Test"
                else:
                    continue

                if current_period and current_period["type"] != period_type:
                    current_period["end"] = e.date.strftime("%Y-%m-%d")
                    periods.append(current_period)
                    current_period = None

                if not current_period:
                    current_period = {
                        "type": period_type,
                        "start": e.date.strftime("%Y-%m-%d"),
                        "end": None,
                        "location": e.site,
                        "start_label": e.event_name,
                    }

            if current_period:
                periods.append(current_period)

            # Add current assignment as an ongoing period if no events infer it
            if d.assignment and (not periods or periods[-1]["type"] == "Repairs"):
                # Find earliest event or use a default start
                start = events[0].date.strftime("%Y-%m-%d") if events and events[0].date else "2025-01-01"
                if periods and periods[-1].get("end"):
                    start = periods[-1]["end"]
                elif periods and not periods[-1].get("end"):
                    pass  # last period is still open
                else:
                    periods.append({
                        "type": d.assignment,
                        "start": start,
                        "end": None,
                        "location": d.current_location,
                        "start_label": d.assignment,
                    })

            timeline_data.append({
                "serial": d.serial_number,
                "name": d.name or d.serial_number,
                "eoat_type": d.eoat_type,
                "assignment": d.assignment,
                "current_location": d.current_location,
                "events": evt_list,
                "periods": periods,
            })

        return render_template(_template("timeline.html"), timeline_data=timeline_data,
                               eoat_types=eoat_types, assignments=assignments)

    @app.route("/api/devices")
    def api_devices():
        devices = EoatDevice.query.order_by(EoatDevice.name).all()
        return jsonify([d.to_dict() for d in devices])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
