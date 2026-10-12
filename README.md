# Waste Management Application Backend

This repository contains a full backend for a waste management application built with Python, FastAPI, SQLAlchemy, MySQL, JWT authentication, and REST APIs.

## Features
- User registration, login, logout, and profile management
- Roles: citizen, collector, admin
- Waste reporting and status tracking
- Collection requests and assignment workflow
- Collector management
- Waste categories and segregation information
- Recycling center information
- Complaint submission and admin review
- Feedback and ratings after completed collections
- Admin dashboard summary statistics

## Tech stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic
- JWT
- Pytest
- Uvicorn

## Project structure
```text
backend/
  app/
    main.py
    database.py
    dependencies.py
    core/
      config.py
      security.py
    models/
      __init__.py
      user.py
      waste_category.py
      waste_report.py
      collection_request.py
      collector_profile.py
      recycling_center.py
      complaint.py
      feedback.py
    schemas/
      __init__.py
      auth.py
      user.py
      waste_management.py
    routers/
      __init__.py
      auth.py
      users.py
      waste_reports.py
      collections.py
      collectors.py
      waste_categories.py
      recycling_centers.py
      complaints.py
      feedback.py
      admin.py
    tests/
      test_api.py
requirements.txt
.env.example
.gitignore
README.md
```

## Setup
1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Create a MySQL database:
```sql
CREATE DATABASE waste_management;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'securepass';
GRANT ALL PRIVILEGES ON waste_management.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
```

5. Start the API:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. Open docs:
```text
http://localhost:8000/docs
```

## Tests
```bash
pytest backend/tests -q
```

## Main routes
- /api/v1/auth
- /api/v1/users
- /api/v1/waste-reports
- /api/v1/collections
- /api/v1/collectors
- /api/v1/waste-categories
- /api/v1/recycling-centers
- /api/v1/complaints
- /api/v1/feedback
- /api/v1/admin
