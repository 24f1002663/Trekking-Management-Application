# Trekking-Management-Application

The Trekking Management Application is a platform where users can explore and book trekking trips online. Admins can manage treks, bookings, and assign staff to different treks. It uses **Flask, Vue.js (Vite), SQLite, Redis, and Celery** to provide a smooth and efficient experience for users and administrators.

## Tech Stack

| Layer      | Technology                                             |
|------------|--------------------------------------------------------|
| Backend    | Flask, Flask-JWT-Extended, Flask-SQLAlchemy            |
| Frontend   | Vue 3 + Vue Router (Vite build), Bootstrap 5           |
| Database   | SQLite (created programmatically via SQLAlchemy)       |
| Caching    | Redis (via Flask-Caching)                              |
| Jobs       | Celery + Celery Beat (Redis broker)                    |
| Email      | Flask-Mail (Gmail SMTP)                                |

## Roles

- **Admin** (pre-seeded, no registration): manage treks, staff, users, bookings, reports. Default login: `admin@trek.com` / `admin123`.
- **Staff** (admin-created, login only): view assigned treks, manage slots/status, view participants.
- **User / Trekker** (self-register): browse & filter open treks, book, view history, export CSV.

## Project Structure

```
backend/            Flask API (app.py, model.py, routes/, scheduler.py, celery_app.py)
frontend/           Vite + Vue 3 SPA (src/, index.html, vite.config.js)
  src/views/        Vue views per page (admin/, staff/, user/, Login, Register)
  static/uploads/   Uploaded trek images (served by Flask at /static/uploads)
api.yaml            OpenAPI 3.0 definition of all endpoints
commands.txt        Exact start commands (for the demo/viva)
```

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A running **Redis** server on `localhost:6379` (required by Celery **and** the API cache).
  On Windows use one of: Memurai, WSL (`sudo apt install redis-server`), or Docker
  (`docker run -d -p 6379:6379 redis`).

## Setup & Run

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:  venv\Scripts\activate      |  macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt

# Email (optional — booking/assignment emails). PowerShell example:
#   $env:MAIL_USERNAME="your@gmail.com"; $env:MAIL_PASSWORD="app_password"

python app.py            # starts the API on http://localhost:8080 and seeds the admin
```

### 2. Background jobs (Redis must be running)

```bash
cd backend
celery -A app.celery worker --pool=solo -l info    # worker (use --pool=solo on Windows)
celery -A app.celery beat -l info                  # scheduler (reminders + monthly report)
```

### 3. Frontend

```bash
cd frontend
npm install

# Development (Vite dev server on :5173, proxies API to Flask :8080):
npm run dev

# Production build (Flask then serves the SPA from frontend/dist at http://localhost:8080):
npm run build
```

Open the dev server at **http://localhost:5173**, or the built app at **http://localhost:8080**.

## Notes

- The database (`backend/instance/trek.db`) and the admin user are created automatically on first run.
- The API caches the open-trek listing in Redis and invalidates it on any booking/trek change.
- Celery Beat sends daily user/staff reminders and a monthly admin report (with an in-app completion notification). To demo a job quickly, lower its schedule in `celery_app.py` or call the task directly.
