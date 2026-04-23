"""EOAT Tracker Dashboard — Flask application."""
from flask import Flask, render_template, jsonify
from config import DATABASE_PATH
from db import db
from models import EoatDevice, EoatEvent


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        from seed import seed_mock_data
        seed_mock_data()

    @app.route("/")
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
        return render_template("dashboard.html", devices=devices,
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
        return render_template("kanban.html", columns=columns)

    @app.route("/device/<serial_number>")
    def device_detail(serial_number):
        device = EoatDevice.query.filter_by(serial_number=serial_number).first_or_404()
        events = EoatEvent.query.filter_by(serial_number=serial_number)\
            .order_by(EoatEvent.date.desc()).all()
        return render_template("device_detail.html", device=device, events=events)

    @app.route("/api/devices")
    def api_devices():
        devices = EoatDevice.query.order_by(EoatDevice.name).all()
        return jsonify([d.to_dict() for d in devices])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
