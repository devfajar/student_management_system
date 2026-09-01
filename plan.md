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

---

### 3. Student Fee & Payment Management System (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Step 1: Write Comprehensive Test Cases First** ([`test_fees.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_fees.py)):
  - [x] `test_fee_structure_crud`: Admin create, list, update, and delete fee structures per course & session.
  - [x] `test_fee_structure_permission`: Non-admins (Staff/Students) forbidden (403) from mutating fee structures.
  - [x] `test_generate_student_invoices`: Bulk generation of fee invoices for all students in a course/session.
  - [x] `test_collect_payment_full`: Recording full payment, updating invoice status to `Paid` and calculating zero balance.
  - [x] `test_collect_payment_partial`: Recording partial payment, updating invoice status to `Partial` and updating remaining balance.
  - [x] `test_collect_payment_overpayment_validation`: Rejecting payment amount exceeding total remaining fee due (400 Bad Request).
  - [x] `test_student_my_invoices`: Student views only their own fee balance, invoice breakdown, and receipts.
  - [x] `test_student_cannot_view_others_invoices`: Strict object-level permission scoping.
  - [x] `test_payment_receipt_details`: Retrieve printable receipt with transaction hash, payer details, and remaining balance.
  - [x] `test_unauthenticated_access`: Rejection with 401 Unauthorized across all endpoints.
- **Step 2: Implement Backend API & Pass Tests**:
  - [x] Database Models: `FeeStructure`, `StudentFeeInvoice`, `FeePayment` with migrations (`0006_feestructure_studentfeeinvoice_feepayment`).
  - [x] Serializers: `FeeStructureSerializer`, `StudentFeeInvoiceSerializer`, `FeePaymentSerializer`.
  - [x] ViewSets & Custom Action Endpoints:
    - `/api/fee-structures/` (CRUD for fee templates)
    - `/api/fees/generate-invoices/` (Bulk invoice generator)
    - `/api/fee-invoices/` (Admin invoice ledger with filters: course, status, student)
    - `/api/fees/my-invoices/` (Student invoices and balance statement)
    - `/api/fees/collect-payment/` (Record transaction)
    - `/api/fees/receipts/:id/` (Receipt details)
  - [x] Execute `manage.py test`: **44/44 tests passing across full codebase**.
- **Step 3: Frontend Integration**:
  - [x] API client methods in `frontend/src/lib/api.js`.
  - [x] Admin View (`ManageFees.svelte`): Fee structure configuration, invoice ledger, payment collection modal with instant receipt generation.
  - [x] Student View (`StudentFees.svelte`): Outstanding balance summary card, invoice list, payment history table, and printable receipt modal.
  - [x] Sidebar and App router integration.

---

## 🔮 Future Integration Roadmap

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

