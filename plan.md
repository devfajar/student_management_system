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

### 4. Redis Caching & Invalidation for High-Frequency Endpoints (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] Configure Redis cache backend (`django_redis.cache.RedisCache`) in `backend/student_management_system/settings.py` with fallback resilience.
  - [x] **RED Phase**: Write test suite in [`test_redis_caching.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_redis_caching.py) checking hit/miss and cache invalidation.
  - [x] **GREEN Phase**: Implement cache helpers in `cache_utils.py` and integrate caching in `dashboard_stats_view`, `CourseViewSet`, `SubjectViewSet`, `SessionYearViewSet`, `StaffViewSet`, `StudentViewSet`, and `FeeStructureViewSet`.
  - [x] Invalidate caches on model mutations (create, update, delete).
  - [x] Verify tests: 100% pass across test suite.

---

### 5. Media & File Management (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] Configure `MEDIA_URL` and `MEDIA_ROOT` in `settings.py` and `urls.py`.
  - [x] Added `profile_pic` to `Staffs`, `Students` and `syllabus_file` to `Subjects` with migration `0007_staffs_profile_pic_subjects_syllabus_file_and_more`.
  - [x] **RED Phase**: Write test suite in [`test_media.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_media.py).
  - [x] **GREEN Phase**: Implement `multipart/form-data` support in `current_user_view`, `SubjectSerializer`, and frontend `api.js`.
  - [x] Frontend avatar uploader in `Profile.svelte` with live photo preview.
  - [x] Verify full test suite: **49/49 tests passing**.

---

### 6. Student Profile Picture & Document Uploads System (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] **RED Phase**: Write test suite in [`test_student_documents.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_student_documents.py):
    - `test_student_upload_document`: Student uploads transcript/certificate/ID with file and metadata.
    - `test_student_can_only_view_own_documents`: Scoped queryset ensures students only access their own files.
    - `test_student_delete_own_document`: Student deletes their own pending/rejected document.
    - `test_admin_can_view_all_documents_with_filters`: Admin lists and filters documents by status/type/course.
    - `test_admin_can_approve_document`: Admin verifies document (`status=1`).
    - `test_admin_can_reject_document_with_reason`: Admin rejects document (`status=2`) with explanatory feedback note.
    - `test_student_cannot_verify_document`: Student attempts to verify document return 403 Forbidden.
  - [x] **GREEN Phase**:
    - Model: `StudentDocument` with fields `student_id`, `document_name`, `document_type`, `document_file`, `verification_status`, `rejection_reason` (migration `0008_studentdocument.py`).
    - Serializer: `StudentDocumentSerializer` with student name, username, course, and type display helpers.
    - ViewSet: `StudentDocumentViewSet` with role-based scoping, file upload, destroy, and `@action(detail=True, methods=['post']) verify`.
    - API URL Registration in `api_urls.py`.
    - Verify all backend tests: **56/56 tests passing (100% GREEN)**.
  - [x] **Frontend Implementation**:
    - Updated `frontend/src/lib/api.js` with document CRUD and verification endpoints (`getStudentDocuments`, `uploadStudentDocument`, `deleteStudentDocument`, `verifyStudentDocument`).
    - Student Document Vault View (`StudentDocuments.svelte`): File uploader with category dropdown, status badges (Approved, Pending, Rejected), feedback display, and preview links.
    - Admin Document Verification Queue (`ManageDocuments.svelte`): Review queue, KPI overview cards, filters (Status, Course, Search), one-click approve, and reject feedback modal.
    - Enhanced `ManageStudents.svelte` with avatar photo uploads and list thumbnails.
    - Enhanced `Navbar.svelte` with live profile picture avatar.
    - Added navigation items to `Sidebar.svelte` and routes to `App.svelte`.
    - Verified frontend build (`bun run build`).

---

### 7. Export & Reporting Engine (PDF & Excel/CSV) (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] Installed `reportlab` in Python virtual environment for PDF rendering.
  - [x] **RED Phase**: Write test suite in [`test_exports.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_exports.py):
    - `test_student_download_own_report_card_pdf`: Student downloads their PDF report card with valid PDF headers.
    - `test_admin_download_any_student_report_card_pdf`: Admin downloads specific student PDF report card.
    - `test_student_cannot_download_other_student_report_card`: Student requesting other student's report card returns 403 Forbidden.
    - `test_admin_export_attendance_csv`: Admin/Staff export attendance report as CSV with status and timestamps.
    - `test_admin_export_fees_csv`: Admin exports student fee invoice ledger with amounts, balances, and payment statuses.
    - `test_admin_export_students_csv`: Admin/Staff export active student roster with details as CSV.
    - `test_student_cannot_export_admin_reports`: Students forbidden from administrative CSV exports (403 Forbidden).
    - `test_unauthenticated_export_denied`: Unauthenticated requests rejected with 401 Unauthorized.
  - [x] **GREEN Phase**:
    - Implemented [`report_utils.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/report_utils.py) with `generate_student_report_card_pdf` generating academic transcript PDFs (institutional header, student details, attendance metrics, examination module scores table, letter grades, GPA, standing summary, and digital signature lines).
    - Added API endpoints in `api_views.py` (`export_report_card_pdf_view`, `export_attendance_csv_view`, `export_fees_csv_view`, `export_students_csv_view`).
    - Registered URL patterns in `api_urls.py`.
    - Verified full backend test suite: **64/64 tests passing (100% GREEN)**.
  - [x] **Frontend Integration**:
    - Added `downloadFile` binary blob helper and export methods (`exportReportCardPdf`, `exportAttendanceCsv`, `exportFeesCsv`, `exportStudentsCsv`) in `frontend/src/lib/api.js`.
    - Integrated "Download Official PDF" in `StudentResults.svelte`.
    - Integrated "Export Attendance CSV" in `ViewAttendance.svelte`.
    - Integrated "Export CSV" in `ManageFees.svelte`.
    - Integrated "Export Roster (CSV)" in `ManageStudents.svelte`.
    - Verified frontend build (`bun run build`).

---

### 8. Automated Silent JWT Token Refresh & Session Keepalive (SMS-5) (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] **RED Phase**: Authored test suite in [`test_jwt_refresh.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_jwt_refresh.py):
    - `test_login_returns_access_and_refresh_tokens`: Login returns valid access and refresh JWTs.
    - `test_token_refresh_produces_valid_new_access_token`: Refresh endpoint yields valid new access token that unlocks protected API endpoints.
    - `test_token_refresh_with_invalid_token_rejected`: Malformed or revoked refresh tokens return 401 Unauthorized.
    - `test_token_refresh_with_missing_payload_rejected`: Empty payloads return 400 Bad Request.
    - `test_expired_or_tampered_token_cannot_access_api`: Tampered authorization headers return 401 Unauthorized.
  - [x] **GREEN Phase & Backend Verification**:
    - Verified full backend test suite: **69/69 tests passing (100% GREEN across 11 test modules)**.
  - [x] **Frontend Silent Refresh & Request Queue System**:
    - Implemented `getRefreshToken()`, `setTokens(access, refresh)`, `clearTokens()`, and `silentRefreshToken()` in [`frontend/src/lib/api.js`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/api.js).
    - Built mutex-guarded `request()` with subscriber callback queue for concurrent request retrying upon token refresh.
    - Added transparent 401 retry handling to binary `downloadFile()` helper.
    - Updated [`authStore.svelte.js`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/authStore.svelte.js) to store dual tokens, listen to `auth:expired` events, and provide proactive keepalive methods.
    - Verified frontend build (`bun run build`).

---

## 🔮 Future Integration Roadmap

### Phase 9: Course Syllabus, Assignments & Student Submission Portal
- Staff post assignments with due dates, attachments, and max scores.
- Students submit digital deliverables.
- Staff review, provide feedback remarks, and record assignment marks directly.

### Phase 10: Staff Salary & Payroll Management Engine
- Base salary configuration by staff tier/designation.
- Monthly payroll generation, deduction/bonus computations, payslip PDF export.

### Phase 11: Docker Containerization
- Multi-stage `Dockerfile` for Django REST API and Svelte frontend.
- `docker-compose.yml` with PostgreSQL 16, Redis, Django DRF Gunicorn backend, and Nginx reverse proxy.





