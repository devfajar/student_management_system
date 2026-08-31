# Student Management System (Django REST Framework + Svelte)

A modernized, decoupled **Student Management System** consisting of a **Django REST Framework (DRF)** backend and a high-performance **Svelte 5** frontend.

---

## 🏗️ Architecture Overview

```
student_management_system/
├── backend/                  # Django REST API Backend
│   ├── manage.py
│   ├── requirements.txt      # Python dependencies
│   ├── student_management_system/  # Core settings, urls, wsgi
│   └── student_management_app/     # Models, serializers, api_views, api_urls
└── frontend/                 # Svelte Single Page Application
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.svelte        # App root router & state coordination
        ├── app.css           # Global modern styling
        └── lib/
            ├── api.js        # Centralized REST API client
            ├── authStore.svelte.js # Reactive auth store
            ├── components/   # Navbar, Sidebar, Modal, StatCard
            └── views/        # Admin, Staff, Student, and Profile views
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** / **Bun**
- **PostgreSQL 14+**

---

### 1. Backend Setup (Django REST Framework)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# (Optional) Create superuser
python manage.py createsuperuser

# Start the DRF backend server (runs on http://127.0.0.1:8000)
python manage.py runserver 0.0.0.0:8000
```

---

### 2. Frontend Setup (Svelte + Vite)

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
bun install
# or: npm install

# Start the Svelte dev server (runs on http://127.0.0.1:5174 or 5173)
bun run dev
# or: npm run dev
```

---

## 🔑 Default Credentials & Roles

| Role | Username / Email | Password | Access / Capabilities |
|---|---|---|---|
| **Admin (HOD)** | `admin` (`admin@example.com`) | `admin123` | Full dashboard, manage staff, students, courses, subjects, sessions, approve leaves, reply feedback, inspect attendance |
| **Staff** | *(Created by Admin)* | *(Set by Admin)* | Staff dashboard, mark attendance, update attendance, apply for leave, submit feedback |
| **Student** | *(Created by Admin)* | *(Set by Admin)* | Student dashboard, view attendance history, apply for leave, submit feedback |

---

## 📡 REST API Endpoints

- **Authentication**: `POST /api/auth/login/`, `POST /api/auth/refresh/`, `GET|PUT /api/auth/me/`
- **Dashboard Metrics**: `GET /api/dashboard/stats/`
- **Staff**: `GET|POST /api/staff/`, `GET|PUT|DELETE /api/staff/:id/`
- **Students**: `GET|POST /api/students/`, `GET|PUT|DELETE /api/students/:id/`
- **Courses**: `GET|POST /api/courses/`, `GET|PUT|DELETE /api/courses/:id/`
- **Subjects**: `GET|POST /api/subjects/`, `GET|PUT|DELETE /api/subjects/:id/`
- **Sessions**: `GET|POST /api/sessions/`, `GET|DELETE /api/sessions/:id/`
- **Leaves**: `GET|POST /api/student-leaves/`, `POST /api/student-leaves/:id/approve/`, `POST /api/student-leaves/:id/disapprove/`, `GET|POST /api/staff-leaves/`, `POST /api/staff-leaves/:id/approve/`, `POST /api/staff-leaves/:id/disapprove/`
- **Feedback**: `GET|POST /api/student-feedback/`, `POST /api/student-feedback/:id/reply/`, `GET|POST /api/staff-feedback/`, `POST /api/staff-feedback/:id/reply/`
- **Attendance**:
  - `GET /api/attendance/get-students/?subject_id=&session_year_id=`
  - `POST /api/attendance/save-attendance/`
  - `GET /api/attendance/get-dates/?subject_id=&session_year_id=`
  - `GET /api/attendance/get-reports/?attendance_id=`
  - `POST /api/attendance/update-attendance/`
  - `GET /api/attendance/student-view/?subject_id=&start_date=&end_date=`