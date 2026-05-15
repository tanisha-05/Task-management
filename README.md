# Task Management Web Application

A lightweight and intuitive web application for managing personal and team tasks. Built with Flask and SQLite, it provides both a user-friendly interface and a robust REST API for integration.

# Features

- User Authentication (Registration & Login)
- Add, Update, Delete Tasks
- Mark Tasks as Complete
- Dashboard Analytics
- REST API Support

# Technologies Used

- Python
- Flask
- SQLite
- SQLAlchemy
- Bootstrap

# Setup & Run Instructions

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Application

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5001
```


# API Endpoints

## Get All Tasks

```http
GET /api/tasks
```

# Response Example

```json
[
  {
    "description": "task management",
    "due_date": "2026-05-15",
    "id": 1,
    "priority": "high",
    "status": "Pending",
    "title": "Project"
  }
]
```

---

## Add Task

```http
POST /api/tasks
```

# Request Example

```json
{
  "title": "Buy stationary",
  "description": "Pencil, eraser",
  "due_date": "2026-05-19",
  "status": "Pending",
  "priority": "low"
}
```

# Response Example

```json
{
  "description": "Pencil, eraser",
  "due_date": "2026-05-19",
  "id": 3,
  "priority": "low",
  "status": "Pending",
  "title": "Buy stationary"
}
```

---

## Update Task

```http
PUT /api/tasks/<id>
```

# Request Example

```json
{
  "priority": "high"
}
```

---

## Delete Task

```http
DELETE /api/tasks/<id>
```

# Response Example

```json
{
  "message": "Task deleted successfully"
}
```

---

## Complete Task

```http
PATCH /api/tasks/<id>/complete
```

# Response Example

```json
{
  "status": "Complete"
}
```