# Development Plan & Feature Roadmap

## 🎯 Current Sprint Goals

### 1. Tailwind CSS Migration
- **Objective**: Standardize styling across all frontend components using Tailwind CSS utility classes and modern responsive layout primitives.
- **Tasks**:
  - [x] Install `tailwindcss`, `postcss`, `autoprefixer` in `frontend/`.
  - [x] Configure `tailwind.config.js` and `postcss.config.js`.
  - [x] Update `src/app.css` with `@tailwind` layers while retaining clean design tokens.
  - [x] Modernize Svelte 5 components (`Navbar`, `Sidebar`, `Modal`, `StatCard`) and views (`Login`, `Profile`, `Admin`, `Staff`, `Student`) with Tailwind utility styling.
  - [x] Verify production build and responsive layout with Playwright.

---

### 2. In-App Notifications & Broadcasts Module
- **Objective**: Full bidirectional notification system allowing administrators to broadcast school-wide or course-specific announcements to students and staff with live in-app badges.
- **Tasks**:
  - [x] **Backend DRF API**:
    - Serializers for `NotificationStudent` and `NotificationStaffs` models.
    - Endpoints:
      - `POST /api/notifications/broadcast-students/`: Broadcast announcement to all students or filtered by course.
      - `POST /api/notifications/broadcast-staff/`: Broadcast announcement to all staff members.
      - `GET /api/notifications/student/`: List current student notifications.
      - `GET /api/notifications/staff/`: List current staff notifications.
      - `GET /api/notifications/admin-history/`: View sent notification broadcast logs.
      - `DELETE /api/notifications/student-notification/:id/` and `DELETE /api/notifications/staff-notification/:id/`.
    - Add automated test cases in `backend/student_management_app/tests/test_notifications.py` (all 38 test suites passing).
  - [x] **Frontend Integration**:
    - Centralize notification REST methods in `frontend/src/lib/api.js`.
    - Add interactive Notification Bell dropdown in `Navbar.svelte` with live unread counter badge and dismiss actions.
    - Admin View (`BroadcastNotification.svelte`): Audience selector (All Students, Specific Course, All Staff), announcement message composer, and history logs table with deletion.
    - Staff & Student Views (`StaffNotifications.svelte`, `StudentNotifications.svelte`): Dedicated circulars/notifications page.
    - Update `Sidebar.svelte` and `App.svelte` routing.

---

## 🔮 Future Integration Roadmap

### Phase 3: Student Fee & Payment Tracking
- Student fee structure by course/session year.
- Fee payment records, invoice receipts, and outstanding balance alerts.

### Phase 4: Media & File Management
- Multipart avatar uploads for student/staff profiles.
- Course syllabus and assignment PDF downloads.

### Phase 5: Automated JWT Token Refresh Interceptor
- Silent token rotation on expiration in `src/lib/api.js` using Axios/Fetch interceptor.

### Phase 6: Export & Reporting Engine
- PDF report cards and Excel/CSV attendance summary sheets.

### Phase 7: Docker Containerization
- `Dockerfile` for Django REST API and Svelte frontend.
- `docker-compose.yml` with PostgreSQL 16, Django DRF Gunicorn backend, and Nginx reverse proxy.
