# Kanban Manager API

A **production-ready backend system** for managing teams, projects, and tasks using the Kanban methodology.  
This project focuses on **real-world backend architecture**, async processing, and operational readiness — not just CRUD APIs.

---

## 🚀 Overview

Kanban Manager API is a **backend-only service** designed to simulate how modern backend systems are built, deployed, and operated in production environments.

The goal of this project is to demonstrate **how backend systems work in real production**, including async jobs, notifications, containerization, and operational concerns.

---

## 🧱 Tech Stack

- **Python**
- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Celery**
- **Redis**
- **JWT Authentication**
- **SMTP (Email Notifications)**
- **Swagger / OpenAPI (drf-spectacular)**
- **Nginx**

---

## ✨ Key Features

- JWT authentication (access & refresh tokens)
- Team management with ownership & roles
- Project-based permissions
- Kanban boards, lists, and tasks
- Task assignment and due dates
- Background email notifications
- Activity tracking per project
- Async processing using Celery
- Scheduled jobs using Celery Beat
- Fully Dockerized architecture

---

## 🔐 Authentication & Security

- JWT-based authentication
- Token refresh support
- Permission-based access control
- Secure production-ready defaults

---

## ⚙️ Architecture Highlights

- Clean separation of Django apps
- Background jobs instead of blocking HTTP requests
- Domain events using signals
- Environment-based configuration
- Scalable Docker-based deployment
- Worker isolation for async processing

---

## 📄 API Documentation

Interactive API documentation available via Swagger:

- **Swagger UI**  
  `http://localhost/api/schema/swagger/`

- **OpenAPI Schema**  
  `http://localhost/api/schema/`



Each module is grouped clearly inside the API:

- `/users/` → authentication, profiles
- `/teams/` → team management & members
- `/projects/` → project ownership & access
- `/boards/` → kanban boards
- `/lists/` → board columns
- `/tasks/` → task lifecycle & ordering
- `/comments/` → task discussions
- `/activity/` → project activity logs
- `/notifications/` → system notifications

This structure makes the API easy to consume, extend, and version over time.

---

## 🧠 Design Decisions (Why This Architecture)

This project was intentionally designed to reflect **how senior backend engineers structure systems**, not just how to “make endpoints work”.

Key decisions:

- **Async-first mindset**  
  Emails and notifications are handled by Celery workers, not HTTP requests.

- **Service isolation**  
  Web app, workers, scheduler, database, cache, and reverse proxy all run in separate containers.

- **Operational readiness**  
  Environment-based configuration, health checks, and predictable startup order.

- **Clear boundaries**  
  Each Django app owns its domain logic without leaking responsibilities.

---

## 🔄 Background Processing (Celery)

The system uses Celery for all time-consuming operations:

- Sending emails
- Due-date reminders
- Task assignment notifications
- Scheduled scans (Celery Beat)

Why this matters:
- Faster API responses
- No blocking requests
- Better scalability
- Production-grade behavior

---

## 🐳 Dockerized Architecture

The entire system runs using Docker Compose with the following services:

- `web` → Django API
- `worker` → Celery worker
- `beat` → Celery scheduler
- `db` → PostgreSQL
- `redis` → Message broker
- `nginx` → Reverse proxy

This setup mirrors real production deployments and makes local development predictable.

---

## 🧪 Testing Philosophy

Tests focus on **behavior**, not just coverage:

- API correctness
- Permission enforcement
- Async task triggering
- Email logic (mocked, no external dependency)

All tests run inside Docker to ensure environment consistency.

---

## 📌 Project Scope & Purpose

This project is intended to:

- Demonstrate backend engineering skills
- Show understanding of async systems
- Reflect real production constraints
- Serve as a strong portfolio backend

It is **not** a tutorial project and **not** frontend-dependent.

---

## 🚧 Future Improvements

Planned enhancements include:

- WebSocket-based real-time updates
- Metrics & monitoring (Prometheus / Grafana)
- CI/CD pipeline
- Object storage integration
- Rate limiting & throttling

---

## 📬 Contact

If you’re interested in backend architecture, async systems, or production-ready APIs, feel free to reach out.

---

End of file.

All endpoints are versioned under:

