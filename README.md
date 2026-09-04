# Student Management System (Django REST Framework + Svelte)

A modern, decoupled **Student Management System (SMS)** built with a **Django REST Framework (DRF)** backend and a high-performance **Svelte 5 + Tailwind CSS** frontend.

---

## 🏗️ Architecture Overview

```
student_management_system/
├── backend/                      # Django REST API Backend
│   ├── manage.py
│   ├── requirements.txt          # Python dependencies (Django 6.1, DRF, JWT, Redis, ReportLab)
│   ├── student_management_system/# Core settings, urls, wsgi, redis cache configs
│   └── student_management_app/   # Models, serializers, api_views, api_urls, report_utils
│       └── tests/                # Comprehensive test suite (64 passing test cases)
└── frontend/                     # Svelte 5 + Tailwind Single Page Application
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── App.svelte            # App root router & state coordination
        ├── app.css               # Tailwind CSS directives
        └── lib/
            ├── api.js            # Centralized REST API & binary download client
            ├── authStore.svelte.js # Svelte 5 reactive auth store
            ├── components/       # Navbar, Sidebar, Modal, StatCard, Badge
            └── views/            # Admin, Staff, Student, and Profile views
```

---

## ✨ Key Features & Capabilities

- 🔐 **JWT Authentication & Role Scoping**: Multi-role system (Admin/HOD, Faculty Staff, Student) with token authentication.
- ⚡ **High-Performance Redis Caching**: Aggressive Redis caching on read-heavy dashboard and notification endpoints with automated cache invalidation.
- 📄 **Academic Transcripts & PDF Generation**: Instant generation of official multi-page PDF report cards using ReportLab featuring student details, attendance metrics, grading breakdown, GPA, and digital verification seal.
- 📊 **Tabular Data Export Engine (CSV)**: Export filtered CSV datasets for attendance logs, student fee invoices & payment ledgers, and active student rosters.
- 📁 **Student Document Vault**: Upload and manage verification files (ID cards, birth certificates, transcripts) with administrative approval/rejection workflows and avatar uploads.
- 💰 **Fee & Payment Management**: Create multi-tier fee structures, batch generate student invoices, collect partial/full payments, and generate printable fee receipts.
- 📝 **Examination & Grading System**: Subject-wise coursework assignment and examination marks recording, letter grade computation, and automated pass/fail evaluation.
- 📢 **In-App Notifications & Circulars**: Role-targeted broadcasts and circulars from administrators to staff and students.
- 📅 **Attendance Tracking**: Subject-specific and academic session-wise attendance tracking and history analysis.
- 🏖️ **Leave & Feedback Workflows**: Student and staff leave requests and feedback systems with approval actions.
- 📖 **Interactive Swagger & ReDoc API Documentation**: Complete OpenAPI 3.0 schema definitions available at `/api/docs/` and `/api/redoc/`.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** / **Bun**
- **PostgreSQL 14+**
- **Redis Server** (for caching)
- **Docker & Docker Compose** (for containerized deployment)

---

### 🐳 Docker Quickstart (Production Orchestration)

Spin up the entire decoupled architecture with a single command:

```bash
# 1. Clone the repository and configure environment variables
cp .env.docker.example .env

# 2. Build and launch all orchestrated services
docker compose up -d --build

# 3. Access the services:
# - Frontend Web Application & Nginx: http://localhost:80
# - Django REST API & Gunicorn:       http://localhost:8000
# - Interactive Swagger API Docs:     http://localhost:80/api/docs/
# - PostgreSQL Database:              localhost:5433 (mapped from 5432)
# - Redis Cache Server:               localhost:6379

# 4. View real-time container logs
docker compose logs -f

# 5. Shut down services
docker compose down
```

---

### 1. Manual Backend Setup (Django REST Framework)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# (Optional) Run the automated 64-test suite
python manage.py test student_management_app.tests

# Start the DRF backend server (runs on http://127.0.0.1:8000)
python manage.py runserver 0.0.0.0:8000
```

---

### 2. Frontend Setup (Svelte 5 + Vite + Tailwind)

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
bun install
# or: npm install

# Start the development server (runs on http://127.0.0.1:5173)
bun run dev
# or: npm run dev

# Or build for production
bun run build
```

---

## 🔑 Default Credentials & Roles

| Role | Username / Email | Password | Access / Capabilities |
|---|---|---|---|
| **Admin (HOD)** | `admin` (`admin@example.com`) | `admin123` | Master dashboard, manage staff, students, courses, subjects, sessions, fee structures, approve leaves, reply feedback, inspect attendance, verify documents, export CSVs |
| **Staff** | *(Created by Admin)* | *(Set by Admin)* | Mark & update attendance, assign coursework and exam grades, apply for leave, submit feedback, export attendance CSV |
| **Student** | *(Created by Admin)* | *(Set by Admin)* | View attendance logs, review academic grades & download official PDF report cards, submit fees, upload documents to vault, apply for leave |

---

## 📡 REST API Reference

### 🔐 Authentication & Profile
- `POST /api/auth/login/`: Token pair generation (access + refresh)
- `POST /api/auth/refresh/`: JWT access token refresh
- `GET|PUT /api/auth/me/`: Current user profile & metadata

### 📊 Dashboard & System Stats (Cached with Redis)
- `GET /api/dashboard/stats/`: Aggregated system KPIs, student gender distributions, course enrollments, and staff counts.

### 📄 Reports & Data Exports (PDF, Excel, CSV, Pagination & Search)
- `GET /api/reports/preview/?type=&search=&page=&page_size=`: Paginated and searchable live records preview (`students`, `attendance`, `fees`, `results`).
- `GET /api/reports/report-card/?student_id=`: Generate official PDF academic transcript (ReportLab).
- `GET /api/reports/attendance-excel/?search=&subject_id=&course_id=`: Export attendance logs as styled Excel (`.xlsx`) workbook.
- `GET /api/reports/attendance-csv/?search=&subject_id=&course_id=`: Export attendance logs as CSV.
- `GET /api/reports/fees-excel/?search=&course_id=&status=`: Export student fee invoice ledger as Excel (`.xlsx`).
- `GET /api/reports/fees-csv/?search=&course_id=&status=`: Export student fee invoice ledger as CSV.
- `GET /api/reports/students-excel/?search=&course_id=`: Export student roster as Excel (`.xlsx`).
- `GET /api/reports/students-csv/?search=&course_id=`: Export student roster as CSV.
- `GET /api/reports/results-excel/?search=&subject_id=`: Export exam results with grades as Excel (`.xlsx`).
- `GET /api/reports/results-csv/?search=&subject_id=`: Export exam results with grades as CSV.

### 📁 Student Document Vault
- `GET|POST /api/student-documents/`: List and upload student verification documents.
- `DELETE /api/student-documents/:id/`: Delete document record.
- `POST /api/student-documents/:id/verify/`: Admin approve or reject document with reason.

### 💰 Fee Management & Invoices
- `GET|POST /api/fee-structures/`: Fee structure templates by course and session.
- `POST /api/fees/generate-invoices/`: Bulk generate invoices for enrolled students.
- `GET /api/fee-invoices/?course_id=&payment_status=`: Query fee invoice records.
- `POST /api/fees/collect-payment/`: Record full or partial fee payments.
- `GET /api/fees/my-invoices/`: Student invoice ledger.
- `GET /api/fees/receipts/:id/`: Printable fee payment receipt.

### 📝 Examination Results & Grading
- `GET|POST /api/results/`: List and manage student results.
- `GET /api/results/get-students/?subject_id=&session_year_id=`: Fetch student grading sheet.
- `POST /api/results/save-results/`: Bulk submit exam and assignment marks.
- `GET /api/results/my-results/`: Student academic transcript summary.

### 📢 In-App Notifications & Circulars
- `GET /api/notifications/student/`: Logged-in student notification feed (Redis cached).
- `GET /api/notifications/staff/`: Logged-in faculty notification feed (Redis cached).
- `POST /api/notifications/broadcast-students/`: Admin broadcast message to students.
- `POST /api/notifications/broadcast-staff/`: Admin broadcast message to faculty.
- `GET /api/notifications/admin-history/`: Broadcast history log.
- `DELETE /api/notifications/student-notification/:id/`: Dismiss student notification.
- `DELETE /api/notifications/staff-notification/:id/`: Dismiss staff notification.

### 👥 Staff, Students, Courses & Sessions
- `GET|POST /api/staff/`, `GET|PUT|DELETE /api/staff/:id/`
- `GET|POST /api/students/`, `GET|PUT|DELETE /api/students/:id/`
- `GET|POST /api/courses/`, `GET|PUT|DELETE /api/courses/:id/`
- `GET|POST /api/subjects/`, `GET|PUT|DELETE /api/subjects/:id/`
- `GET|POST /api/sessions/`, `GET|DELETE /api/sessions/:id/`

### 📅 Attendance Logs
- `GET /api/attendance/get-students/?subject_id=&session_year_id=`
- `POST /api/attendance/save-attendance/`
- `GET /api/attendance/get-dates/?subject_id=&session_year_id=`
- `GET /api/attendance/get-reports/?attendance_id=`
- `POST /api/attendance/update-attendance/`
- `GET /api/attendance/student-view/?subject_id=&start_date=&end_date=`

### 🏖️ Leaves & Feedback
- `GET|POST /api/student-leaves/`, `POST /api/student-leaves/:id/approve/`, `POST /api/student-leaves/:id/disapprove/`
- `GET|POST /api/staff-leaves/`, `POST /api/staff-leaves/:id/approve/`, `POST /api/staff-leaves/:id/disapprove/`
- `GET|POST /api/student-feedback/`, `POST /api/student-feedback/:id/reply/`
- `GET|POST /api/staff-feedback/`, `POST /api/staff-feedback/:id/reply/`

### 💼 Staff Salary & Payroll Management (SMS-13)
- `GET|POST /api/staff-salaries/`: List, configure, and manage staff salary packages and tiers.
- `GET /api/staff-salaries/my_salary/`: Authenticated staff member views own salary structure.
- `GET|POST /api/staff-payrolls/`: Monthly payroll ledger with search, status, and month/year filters.
- `POST /api/staff-payrolls/batch_generate/`: Automated monthly payroll batch calculation for all active faculty.
- `POST /api/staff-payrolls/:id/mark_paid/`: Mark payroll disbursement as Paid with method and transaction ref.
- `GET /api/staff-payrolls/:id/download_payslip_pdf/`: Download official verified ReportLab salary payslip PDF.
- `GET /api/staff-payrolls/export_excel/`: Export payroll ledger as formatted OpenPyXL Excel spreadsheet.
- `GET /api/staff-payrolls/export_csv/`: Export payroll ledger as CSV dataset.
- `GET /api/staff-payrolls/stats/`: Key financial metrics (total disbursed, pending payouts, record counts).

---

## 🧪 Testing (TDD Driven)

The backend features a test suite covering authentication, permissions, models, endpoints, data integrity, and error states:

```bash
cd backend
python manage.py test student_management_app.tests
```

**Test Coverage**:
- `test_auth.py`: 6 tests (JWT, permissions, token refresh)
- `test_courses_subjects.py`: 6 tests (Course & Subject CRUD, constraints)
- `test_students_staff.py`: 8 tests (Registration, profile management)
- `test_attendance.py`: 5 tests (Attendance logging, date queries, filters)
- `test_leaves_feedback.py`: 8 tests (Applications, approvals, replies)
- `test_results.py`: 5 tests (Grading, score updates, student transcript view)
- `test_notifications.py`: 6 tests (Broadcasts, circulars, caching, deletion)
- `test_fees.py`: 5 tests (Fee templates, bulk invoice generation, payment collection)
- `test_student_documents.py`: 7 tests (Document upload, MIME types, verification workflows)
- `test_exports.py`: 8 tests (Report card PDF generation, CSV exports, permission barriers)
- `test_jwt_refresh.py`: 5 tests (Token issuance, refresh lifecycle, tamper checks)
- `test_assignments.py`: 8 tests (Coursework posting, student submissions, late detection, grading)
- `test_reports_excel_pagination.py`: 9 tests (Excel `.xlsx` generation, search filtering, server-side pagination, role barriers)
- `test_staff_payroll.py`: 12 tests (Salary tiers, monthly payroll runs, payslip PDF generation, Excel/CSV exports, role barriers)

**Total**: **98 / 98 passing tests (100% OK across 14 test suites)**