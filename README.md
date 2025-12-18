Kanban Manager API

A production-ready backend system for managing teams, projects, and tasks using the Kanban methodology.
This project focuses on real-world backend architecture, async processing, and operational readiness — not just CRUD APIs.

🚀 Overview

Kanban Manager API is a backend-only service designed to simulate how modern backend systems are built, deployed, and operated in production environments.

The project emphasizes:

Clean architecture

Async background processing

Environment-based configuration

Dockerized workflows

Clear API contracts

🏗️ Tech Stack

Python / Django

Django REST Framework

PostgreSQL

Docker & Docker Compose

Celery + Redis

JWT Authentication

SMTP (Email notifications)

Swagger / OpenAPI (drf-spectacular)

✨ Key Features

User authentication (JWT access & refresh tokens)

Teams & role-based permissions

Projects with members and ownership

Kanban boards with lists and tasks

Task assignment & due-date tracking

Asynchronous notifications (email & in-app)

Activity logging across projects

Background jobs & scheduled tasks (Celery Beat)

Fully dockerized environment (web, worker, beat, db, redis, nginx)

🔐 Authentication

JWT-based authentication

Token rotation & blacklist support

Secure production defaults

Throttling & permission enforcement

⚙️ Architecture Highlights

Separation of concerns between apps

Async processing using Celery instead of blocking HTTP requests

Signals for domain events (task assignment, due dates, activity logging)

Environment-driven configuration (.env)

Safe database migrations (single migration runner)

Production-aware settings (security headers, throttling)

📄 API Documentation

Interactive API documentation is available via Swagger:

Swagger UI:
http://localhost/api/schema/swagger/

OpenAPI Schema (JSON):
http://localhost/api/schema/

All endpoints are namespaced under:

/api/v1/

🐳 Running Locally (Docker)
1. Clone the repository
git clone https://github.com/USERNAME/kanban-manager-api.git
cd kanban-manager-api

2. Create environment file
cp .env.example .env


Edit .env if needed (database, SMTP, secrets).

3. Build & start services
docker compose build
docker compose up -d

4. Apply migrations

Migrations are applied automatically by the web container at startup.

5. Access services

API: http://localhost

Swagger: http://localhost/api/schema/swagger/

PostgreSQL: exposed internally via Docker

Redis: 6379

🧪 Testing

Run the test suite inside Docker:

docker compose exec web python manage.py test -v 2


Tests cover:

Core API flows

Notifications

Email tasks (SMTP mocked)

Activity logging

Permissions

📬 Email & Notifications

SMTP-based email notifications

Celery-powered async delivery

Email templates (HTML + text)

Safe deduplication for due-date reminders

Debug preview endpoints (development only)

🔒 Security Notes

.env is not committed

Secure defaults enforced when DEBUG=False

JWT refresh token rotation enabled

CORS & throttling configurable via environment variables

📌 Project Status

✅ Core backend features implemented
✅ Docker & async processing ready
✅ API fully documented
✅ Suitable as a backend portfolio project

Future improvements:

WebSocket / real-time updates

File storage (S3-compatible)

CI/CD pipeline

Metrics & monitoring (Prometheus / Sentry)

👤 Author

Backend Engineer
Focused on Django, scalable APIs, and production-ready systems.
