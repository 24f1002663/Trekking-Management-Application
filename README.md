# Trekking Management Application

This project is a trekking management system built using Flask and Vue.js. It allows users to browse and book treks, while admins can manage treks, users, bookings, and staff. Staff members can view the treks assigned to them and update trek-related information.

The application also uses Redis for caching and Celery for background tasks like reminder emails and monthly reports.

## Tech Stack

| Layer           | Technology                                  |
| --------------- | ------------------------------------------- |
| Backend         | Flask, Flask-SQLAlchemy, Flask-JWT-Extended |
| Frontend        | Vue 3 (Vite), Vue Router, Bootstrap 5       |
| Database        | SQLite                                      |
| Caching         | Redis (Flask-Caching)                       |
| Background Jobs | Celery + Celery Beat                        |
| Email           | Flask-Mail (Gmail SMTP)                     |

## User Roles

### Admin

* Default account is created automatically.
* Can manage users, staff, treks, bookings, and reports.
* Default login:

  * Email: `admin@trek.com`
  * Password: `admin123`

### Staff

* Created by the admin.
* Can view assigned treks.
* Can update trek status and view participant details.

### User

* Can register and log in.
* Browse available treks.
* Book treks.
* View booking history.
* Export booking history as CSV.

## Project Structure

```text
backend/
    app.py
    model.py
    routes/
    scheduler.py
    celery_app.py

frontend/
    src/
    static/uploads/

api.yaml
commands.txt
```

## Requirements

* Python 3.10 or above
* Node.js 18+
* Redis running on `localhost:6379`

## Running the Project

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

The backend starts on:

```
http://localhost:8080
```

If you want email notifications to work, set these environment variables before starting the server:

```bash
export MAIL_USERNAME="your_email"
export MAIL_PASSWORD="your_app_password"
```

### Celery Worker

```bash
cd backend

celery -A app.celery worker --pool=solo -l info
```

### Celery Beat

```bash
cd backend

celery -A app.celery beat -l info
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

The frontend runs on:

```
http://localhost:5173
```

To build the production version:

```bash
npm run build
```

## Features

* User registration and login using JWT.
* Browse and book trekking events.
* Admin dashboard for managing treks, users, staff, and bookings.
* Staff dashboard for assigned treks.
* Image upload for treks.
* Booking history with CSV export.
* Redis caching for open trek listings.
* Daily reminder emails and monthly reports using Celery.

## Notes

* The SQLite database is created automatically the first time the application runs.
* The default admin account is also created automatically.
* Redis is used for both caching and Celery.
* Email notifications work with Gmail SMTP using an App Password.

---

This project was developed as part of the Modern Application Development course. The main goal was to build a complete full-stack application while learning authentication, REST APIs, background jobs, caching, and frontend-backend integration.
