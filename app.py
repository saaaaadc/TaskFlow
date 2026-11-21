"""
Task Manager REST API
----------------------
A simple CRUD API built with Flask + SQLAlchemy.

Endpoints:
  GET    /tasks          -> list all tasks
  GET    /tasks/<id>     -> get a single task
  POST   /tasks          -> create a new task
  PUT    /tasks/<id>     -> update an existing task
  DELETE /tasks/<id>     -> delete a task

Run with: python app.py
"""

import logging
from datetime import date
from flask import Flask, request, jsonify
from models import db, Task

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

def create_app(db_uri="sqlite:///tasks.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


# Basic logging setup — every request that causes an error gets logged.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("task_api")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def register_routes(app):

    @app.route("/tasks", methods=["GET"])
    def get_tasks():
        tasks = Task.query.all()
        return jsonify([t.to_dict() for t in tasks]), 200

    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            logger.warning(f"GET /tasks/{task_id} - not found")
            return jsonify({"error": f"Task {task_id} not found"}), 404
        return jsonify(task.to_dict()), 200

    @app.route("/tasks", methods=["POST"])
    def create_task():
        data = request.get_json(silent=True)

        # ---- Input validation ----
        if not data:
            logger.warning("POST /tasks - no JSON body received")
            return jsonify({"error": "Request body must be valid JSON"}), 400

        title = data.get("title")
        if not title or not isinstance(title, str) or not title.strip():
            logger.warning("POST /tasks - missing or invalid 'title'")
            return jsonify({"error": "'title' is required and must be a non-empty string"}), 400

        status = data.get("status", "pending")
        priority = data.get("priority", "medium")
        valid_priorities = {"low", "medium", "high"}
        if priority not in valid_priorities:
            return jsonify({"error": "priority must be low, medium, or high"}), 400
        valid_statuses = {"pending", "in_progress", "completed"}
        if status not in valid_statuses:
            logger.warning(f"POST /tasks - invalid status '{status}'")
            return jsonify({"error": f"'status' must be one of {sorted(valid_statuses)}"}), 400
            
        due_date_value = data.get("due_date")
        if due_date_value is not None:
            if not isinstance(due_date_value, str):
                return jsonify({"error": "due_date must be in YYYY-MM-DD format"}), 400

            try:
                due_date_value = date.fromisoformat(due_date_value)
            except ValueError:
                return jsonify({"error": "due_date must be a valid date in YYYY-MM-DD format"}), 400
            
        task = Task(
            title=title.strip(),
            description=data.get("description"),
            status=status,
            priority=priority,
            due_date=due_date_value
        )
        db.session.add(task)
        db.session.commit()
        logger.info(f"Created task {task.id}: {task.title}")
        return jsonify(task.to_dict()), 201

    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            logger.warning(f"PUT /tasks/{task_id} - not found")
            return jsonify({"error": f"Task {task_id} not found"}), 404

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        if "title" in data:
            if not data["title"] or not isinstance(data["title"], str) or not data["title"].strip():
                return jsonify({"error": "'title' must be a non-empty string"}), 400
            task.title = data["title"].strip()

        if "description" in data:
            task.description = data["description"]

        if "status" in data:
            valid_statuses = {"pending", "in_progress", "completed"}
            if data["status"] not in valid_statuses:
                return jsonify({"error": f"'status' must be one of {sorted(valid_statuses)}"}), 400
            task.status = data["status"]

        if "priority" in data:
            valid_priorities = {"low", "medium", "high"}
            if data["priority"] not in valid_priorities:
                return jsonify({"error":"priority must be low, medium, or high"}), 400
            task.priority = data["priority"]

        if "due_date" in data:
            due_date_value = data["due_date"]

            if due_date_value is None:
                task.due_date = None
            elif not isinstance(due_date_value, str):
                return jsonify({"error": "due_date must be in YYYY-MM-DD format"}), 400
            else:
                try:
                    task.due_date = date.fromisoformat(due_date_value)
                except ValueError:
                    return jsonify({"error": "due_date must be a valid date in YYYY-MM-DD format"}), 400

        db.session.commit()
        logger.info(f"Updated task {task.id}")
        return jsonify(task.to_dict()), 200

    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            logger.warning(f"DELETE /tasks/{task_id} - not found")
            return jsonify({"error": f"Task {task_id} not found"}), 404

        db.session.delete(task)
        db.session.commit()
        logger.info(f"Deleted task {task_id}")
        return jsonify({"message": f"Task {task_id} deleted"}), 200

    # ---- Generic error handlers ----
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

