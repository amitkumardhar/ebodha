# eBodha - Academic Information Management System

eBodha is an academic management system designed for executive program students. It tracks student progress, grades, transcripts, and allows teachers and administrators to manage academic activities.

## Technology Stack

*   **Backend Framework**: FastAPI (Python)
*   **Relational Database**: PostgreSQL (for structured data like users, courses, grades)
*   **NoSQL Database**: MongoDB (for activity logs)
*   **ORM**: SQLAlchemy (PostgreSQL), Beanie (MongoDB)
*   **Containerization**: Docker & Docker Compose

## Directory Structure

```
ebodha/
├── app/
│   ├── api/            # API endpoints (v1)
│   ├── core/           # Core config, security, middleware
│   ├── db/             # Database connection & session handling
│   ├── models/         # SQLAlchemy & Beanie models
│   ├── schemas/        # Pydantic schemas for validation
│   └── main.py         # Application entry point
├── docker-compose.yml  # Docker services configuration
├── Dockerfile          # API container definition
└── requirements.txt    # Python dependencies
```

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose

### Running the Application

1.  **Clone the repository** (if applicable).

2.  **Build and start the services**:
    ```bash
    docker-compose up --build
    ```

    This command will start three containers:
    *   `web`: The FastAPI backend (exposed on port 8000)
    *   `db`: PostgreSQL database (exposed on port 5432)
    *   `mongo`: MongoDB database (exposed on port 27017)

3.  **Access the API Documentation**:
    Once the services are running, open your browser and navigate to:
    *   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Features

*   **Authentication**: OAuth2 with Password flow (JWT).
*   **User Management**: Create and manage students, teachers, alumni, and admins.
*   **Academic Management**: Manage semesters, courses, and offerings.
*   **Registration**: Students can register for courses.
*   **Examinations & Grading**: Teachers can create exams, upload marks, and assign grades.
*   **Bulk Upload**: Support for bulk uploading course offerings, registrations, marks, and grades via CSV.
*   **Logging**: All API requests are logged to MongoDB.

## Development

To run the application locally without Docker (requires local PostgreSQL and MongoDB):

1.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the server:
    ```bash
    uvicorn app.main:app --reload
    ```
