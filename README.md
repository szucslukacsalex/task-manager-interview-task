# Task Management API

A modern, RESTful API for task management built with FastAPI, SQLite, and SQLAlchemy. This application provides endpoints for creating, retrieving, updating, and deleting tasks, as well as smart task suggestions.

## Features

- RESTful API design with FastAPI
- SQLite database with SQLAlchemy ORM
- Task CRUD operations
- Filtering and sorting capabilities
- Smart task suggestions
- API documentation with Swagger UI
- Proper error handling and validation

## Setup Instructions

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/task-manager-interview-task.git
cd task-manager-interview-task
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required dependencies:

```bash
cd task-management-api
pip install -r requirements.txt
```

### Running the API

Start the API server:

```bash
python -m app.main
```

The API will be available at http://localhost:8000

You can access the Swagger UI documentation at http://localhost:8000/docs or the alternative ReDoc documentation at http://localhost:8000/redoc.

## API Endpoints

### Root Endpoint

```
GET /
```

Returns a welcome message.

**Response Example:**
```json
{
  "message": "Welcome to the Task Management API!"
}
```

### Tasks

#### Create a New Task

```
POST /tasks
```

Creates a new task in the system.

**Request Body:**
```json
{
  "title": "Complete project proposal",
  "description": "Finish drafting the project proposal for the client meeting",
  "due_date": "2025-06-15T14:00:00Z",
  "status": "pending"
}
```

**Response Example:**
```json
{
  "id": 1,
  "title": "Complete project proposal",
  "description": "Finish drafting the project proposal for the client meeting",
  "due_date": "2025-06-15T14:00:00Z",
  "status": "pending",
  "creation_date": "2025-06-04T08:30:00Z"
}
```

#### Get All Tasks

```
GET /tasks
```

Retrieves all tasks with optional filtering and sorting parameters.

**Query Parameters:**
- `status` (optional): Filter by task status (`pending`, `in_progress`, `completed`)
- `due_date` (optional): Filter by due date (ISO format)
- `sort_by` (optional): Field to sort by (`creation_date`, `due_date`), defaults to `creation_date`
- `sort_order` (optional): Sort order (`asc`, `desc`), defaults to `asc`
- `limit` (optional): Maximum number of tasks to return (1-100)
- `offset` (optional): Number of tasks to skip, defaults to 0

**Response Example:**
```json
[
  {
    "id": 1,
    "title": "Complete project proposal",
    "description": "Finish drafting the project proposal for the client meeting",
    "due_date": "2025-06-15T14:00:00Z",
    "status": "pending",
    "creation_date": "2025-06-04T08:30:00Z"
  },
  {
    "id": 2,
    "title": "Schedule client meeting",
    "description": "Set up a meeting with the client to discuss requirements",
    "due_date": "2025-06-10T10:00:00Z",
    "status": "completed",
    "creation_date": "2025-06-03T14:15:00Z"
  }
]
```

#### Get a Specific Task

```
GET /tasks/{task_id}
```

Retrieves a specific task by ID.

**Response Example:**
```json
{
  "id": 1,
  "title": "Complete project proposal",
  "description": "Finish drafting the project proposal for the client meeting",
  "due_date": "2025-06-15T14:00:00Z",
  "status": "pending",
  "creation_date": "2025-06-04T08:30:00Z"
}
```

#### Update a Task

```
PATCH /tasks/{task_id}
```

Updates an existing task. Only the fields included in the request body will be updated.

**Request Body:**
```json
{
  "status": "in_progress",
  "description": "Updated description with additional details"
}
```

**Response Example:**
```json
{
  "id": 1,
  "title": "Complete project proposal",
  "description": "Updated description with additional details",
  "due_date": "2025-06-15T14:00:00Z",
  "status": "in_progress",
  "creation_date": "2025-06-04T08:30:00Z"
}
```

#### Delete a Task

```
DELETE /tasks/{task_id}
```

Deletes a task by ID. Returns a 204 No Content response on success.

### Smart Suggestions

#### Get Task Suggestions

```
GET /tasks/suggest
```

Retrieves smart task suggestions based on user context and preferences.

**Query Parameters:**
- `limit` (optional): Maximum number of suggestions to return (1-10), defaults to 5

**Response Example:**
```json
[
  {
    "suggested_title": "Review yesterday's meeting notes",
    "suggested_description": "Go through the meeting notes and extract action items",
    "confidence_score": 0.92,
    "reasoning": "Based on your past task patterns, you often review notes after meetings"
  },
  {
    "suggested_title": "Follow up with client emails",
    "suggested_description": "Check and respond to client emails from yesterday",
    "confidence_score": 0.85,
    "reasoning": "You typically respond to emails within 24 hours"
  }
]
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

**Error Response Example:**
```json
{
  "detail": "Task not found"
}
```

## Notes

- All datetime fields use ISO 8601 format in UTC timezone
- Task titles must be between 1-200 characters
- Task descriptions have a maximum length of 500 characters
- Due dates must be in the future
