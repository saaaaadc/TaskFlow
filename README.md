# Task Manager REST API

A simple CRUD REST API for managing tasks, built with Flask and SQLAlchemy.
Supports creating, reading, updating, and deleting tasks, backed by a SQLite database.

## Features

- Full CRUD operations (Create, Read, Update, Delete)
- Input validation with clear error messages
- Structured error handling (400, 404, 500 responses)
- Request logging
- Unit test suite covering all endpoints (pytest)

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy (ORM)
- SQLite (default; can be swapped for MySQL/PostgreSQL by changing the DB URI)
- pytest

## Setup

1. Clone the repository:
   ```
   git clone <your-repo-url>
   cd task-api
   ```

2. Create a virtual environment (recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the app:
   ```
   python app.py
   ```

   The API will be available at `http://127.0.0.1:5000`.

## Running Tests

```
pytest -v
```

## API Endpoints

| Method | Endpoint         | Description           |
|--------|------------------|------------------------|
| GET    | /tasks           | List all tasks         |
| GET    | /tasks/<id>      | Get a single task      |
| POST   | /tasks           | Create a new task      |
| PUT    | /tasks/<id>      | Update an existing task|
| DELETE | /tasks/<id>      | Delete a task          |

## Example Requests

**Create a task:**
```bash
curl -X POST http://127.0.0.1:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Finish resume", "status": "in_progress"}'
```

**Get all tasks:**
```bash
curl http://127.0.0.1:5000/tasks
```

**Update a task:**
```bash
curl -X PUT http://127.0.0.1:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

**Delete a task:**
```bash
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

## Project Structure

```
task-api/
├── app.py          # Flask app and route definitions
├── models.py       # SQLAlchemy database models
├── test_app.py     # Unit tests (pytest)
├── requirements.txt
└── README.md
```
