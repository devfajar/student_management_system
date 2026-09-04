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

### 9. Course Syllabus, Assignments & Student Submission Portal (SMS-6) (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] **RED Phase**: Authored test suite in [`test_assignments.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_assignments.py):
    - `test_staff_create_assignment_success`: Staff publish assignments with due dates, attachments, and max marks.
    - `test_student_cannot_create_assignment`: Students barred with 403 Forbidden from creating assignments.
    - `test_student_list_assignments_for_enrolled_course`: Scoped to student's enrolled courses.
    - `test_student_submit_assignment_on_time`: Student submit deliverable text and file with status 'Submitted' and `is_late=False`.
    - `test_student_submit_assignment_late_detection`: Automatic detection marking submission `is_late=True` when past deadline.
    - `test_staff_grade_submission_success`: Staff evaluate submission, award marks, write feedback remarks, and mark status 'Graded'.
    - `test_student_cannot_grade_submission`: Students forbidden from self-grading with 403 Forbidden.
    - `test_unauthenticated_assignment_access_denied`: 401 Unauthorized for anonymous requests.
  - [x] **GREEN Phase & Backend Verification**:
    - Created `Assignment` and `StudentAssignmentSubmission` models in [`models.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/models.py).
    - Created and ran migration `0009_assignment_studentassignmentsubmission`.
    - Added `AssignmentSerializer` and `StudentAssignmentSubmissionSerializer` in [`serializers.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/serializers.py).
    - Created `AssignmentViewSet` and `StudentAssignmentSubmissionViewSet` in [`api_views.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/api_views.py).
    - Registered routers in [`api_urls.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/api_urls.py).
    - Verified full test suite: **77/77 tests passing (100% GREEN across 12 test modules)**.
  - [x] **Frontend Integration**:
    - Added API endpoints in [`api.js`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/api.js): `getAssignments`, `createAssignment`, `deleteAssignment`, `getAssignmentSubmissions`, `submitAssignment`, `getMyAssignmentSubmissions`, `gradeAssignmentSubmission`.
    - Implemented [`ManageAssignments.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/views/staff/ManageAssignments.svelte) for Staff & Admins.
    - Implemented [`StudentAssignments.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/views/student/StudentAssignments.svelte) for Students.
    - Integrated navigation and view routing in [`App.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/App.svelte) and [`Sidebar.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/components/Sidebar.svelte).
    - Verified production build: `bun run build` (0 errors).

---

### 10. Multi-Format Reports & Export Engine (PDF, Excel, CSV) with Server-Side Pagination & Search (SMS-7) (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] **RED Phase**: Created [`test_reports_excel_pagination.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_reports_excel_pagination.py):
    - `test_admin_export_attendance_excel`: Attendance `.xlsx` openpyxl generation with headers, thin borders, status badges.
    - `test_admin_export_fees_excel`: Fee ledger `.xlsx` with balance amounts and invoice identifiers.
    - `test_admin_export_students_excel`: Student roster `.xlsx` with enrollment details and credentials.
    - `test_admin_export_results_excel`: Academic exam results `.xlsx` with scores, grades, and pass/fail standing.
    - `test_excel_export_filtered_by_search`: Validates query search parameter accurately filters workbook contents.
    - `test_paginated_reports_preview_endpoint`: Validates `CustomPagination` metadata (`count`, `total_pages`, `current_page`, `page_size`, `results`).
    - `test_paginated_reports_search_filtering`: Validates dynamic `Q(...)` search on previews.
    - `test_student_forbidden_from_admin_excel_exports`: Barred with `403 Forbidden`.
    - `test_unauthenticated_export_denied`: Guarded with `401 Unauthorized`.
  - [x] **GREEN Phase & Backend Verification**:
    - Added `openpyxl==3.1.5` to `requirements.txt` and python venv.
    - Built Excel generation functions in [`report_utils.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/report_utils.py) with navy header styling, thin borders, and auto column widths.
    - Implemented `CustomPagination` and `reports_preview_view` in [`api_views.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/api_views.py).
    - Implemented `export_attendance_excel_view`, `export_fees_excel_view`, `export_students_excel_view`, `export_results_excel_view`, and `export_results_csv_view`.
    - Added query `search` filtering across all Excel and CSV endpoints.
    - Registered routes in [`api_urls.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/api_urls.py).
    - Verified full test suite: **86/86 tests passing (100% GREEN across all 13 test suites)**.
  - [x] **Frontend Integration**:
    - Added API endpoints in [`api.js`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/api.js): `getReportsPreview`, `exportAttendanceExcel`, `exportFeesExcel`, `exportStudentsExcel`, `exportResultsExcel`, `exportResultsCsv`.
    - Created [`ReportsCenter.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/views/admin/ReportsCenter.svelte) with multi-tab selector, live debounce query search, filter toolbar, multi-format export buttons, and paginated table with rows-per-page selector.
    - Integrated navigation routing in [`App.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/App.svelte) and [`Sidebar.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/components/Sidebar.svelte).
    - Verified frontend compilation: `bun run build` (0 errors).

---

### 11. Staff Salary & Payroll Management Engine (SMS-13) (TDD Driven)
- **Methodology**: Test-Driven Development (Red $\rightarrow$ Green $\rightarrow$ Refactor)
- **Tasks**:
  - [x] **RED Phase**: Authored test suite in [`test_staff_payroll.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_staff_payroll.py) covering 12 unit and integration tests:
    - `test_admin_create_staff_salary_structure`: Admin configures base salary, allowance, designation, and tax rate.
    - `test_staff_view_own_salary_structure`: Staff views their own configured salary tier.
    - `test_staff_cannot_view_or_modify_other_staff_salary`: Isolation check barring staff from other staff packages.
    - `test_admin_generate_individual_monthly_payroll`: Admin creates individual payroll with bonus and deduction calculations.
    - `test_admin_batch_generate_monthly_payroll`: Admin runs automated monthly payroll run for all active faculty.
    - `test_admin_update_payroll_payment_status`: Admin marks payroll as Paid with payment method and disbursement date.
    - `test_staff_view_own_payroll_history`: Scoped queryset ensures staff only see their own payslips.
    - `test_staff_download_own_payslip_pdf`: Staff downloads verifiable official PDF payslip.
    - `test_staff_cannot_download_other_staff_payslip_pdf`: Security barrier preventing downloading other staff payslips (403 Forbidden).
    - `test_student_forbidden_from_payroll_endpoints`: Students barred with 403 Forbidden.
    - `test_unauthenticated_payroll_access_denied`: Anonymous requests rejected with 401 Unauthorized.
    - `test_admin_export_payroll_excel_and_csv`: Admin exports monthly payroll ledgers as Excel (.xlsx) and CSV.
  - [x] **GREEN Phase & Backend Verification**:
    - Created `StaffSalary` and `StaffPayroll` models in [`models.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/models.py).
    - Applied migration `0010_staffsalary_staffpayroll.py`.
    - Implemented `StaffSalarySerializer` and `StaffPayrollSerializer` in [`serializers.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/serializers.py).
    - Implemented `generate_payslip_pdf_bytes`, `generate_payroll_excel_bytes`, and `generate_payroll_csv_bytes` in [`report_utils.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/report_utils.py).
    - Implemented `StaffSalaryViewSet` and `StaffPayrollViewSet` with `IsAdminOrStaff` permissions, batch generation, mark-as-paid, PDF download, and export actions in [`api_views.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/api_views.py).
    - Registered endpoints in [`api_urls.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/api_urls.py).
    - Verified full backend test suite: **98/98 tests passing (100% GREEN across 14 test modules in 258s)**.
  - [x] **Frontend Implementation**:
    - Added API endpoints in [`api.js`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/api.js): `getStaffSalaries`, `createStaffSalary`, `updateStaffSalary`, `getMySalary`, `getStaffPayrolls`, `getPayrollStats`, `batchGeneratePayroll`, `markPayrollPaid`, `exportPayslipPdf`, `exportPayrollExcel`, `exportPayrollCsv`.
    - Built Admin Payroll Center ([`ManagePayroll.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/views/admin/ManagePayroll.svelte)): KPI cards, monthly ledger, filters, batch generation modal, payment disbursement modal, and Excel/CSV exports.
    - Built Staff Compensation Portal ([`MyPayslips.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/views/staff/MyPayslips.svelte)): Active compensation tier card, disbursement history table, and instant official PDF payslip downloads.
    - Integrated routing and navigation in [`App.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/App.svelte) and [`Sidebar.svelte`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/src/lib/components/Sidebar.svelte).
    - Verified frontend compilation: `bun run build` (0 errors, 3,803 modules transformed).

---

### 12. Full Production Docker Containerization & Orchestration (SMS-17)
- **Tasks**:
  - [x] Configured dynamic environment variables in [`settings.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_system/settings.py) for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASES`, and Redis caching.
  - [x] Added `gunicorn==26.2.0` to [`requirements.txt`](file:///home/lenovo/Documents/my_project/student_management_system/backend/requirements.txt).
  - [x] Created production backend Dockerfile ([`backend/Dockerfile`](file:///home/lenovo/Documents/my_project/student_management_system/backend/Dockerfile)) based on Python 3.12-slim with system libraries (`gcc`, `libpq-dev`, `libjpeg-dev`, `zlib1g-dev`, `libfreetype6-dev`).
  - [x] Created entrypoint script ([`backend/entrypoint.sh`](file:///home/lenovo/Documents/my_project/student_management_system/backend/entrypoint.sh)) with automated database TCP readiness check, migration execution, and static collection.
  - [x] Created multi-stage frontend Dockerfile ([`frontend/Dockerfile`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/Dockerfile)) with Bun 1.x builder stage and Nginx Alpine runtime.
  - [x] Created Nginx reverse proxy configuration ([`frontend/nginx.conf`](file:///home/lenovo/Documents/my_project/student_management_system/frontend/nginx.conf)) with SPA client routing, Gzip compression, and reverse proxying for `/api/`, `/media/`, `/admin/`, and `/static/`.
  - [x] Created complete multi-service orchestration ([`docker-compose.yml`](file:///home/lenovo/Documents/my_project/student_management_system/docker-compose.yml)):
    - `db`: PostgreSQL 16 Alpine with persistent volume and healthcheck.
    - `redis`: Redis 7 Alpine with healthcheck.
    - `backend`: Django DRF Gunicorn app with volume mounts for media and static files.
    - `frontend`: Nginx + Svelte bundle exposing port 80.
  - [x] Created [`.env.docker.example`](file:///home/lenovo/Documents/my_project/student_management_system/.env.docker.example) and [`.dockerignore`](file:///home/lenovo/Documents/my_project/student_management_system/.dockerignore) files.
  - [x] Verified Docker builds with `docker compose build`: **Both backend and frontend images built successfully (0 errors)**.

---

### 13. Automated CI/CD Pipeline via GitHub Actions (SMS-18)
- **Tasks**:
  - [x] Created multi-job workflow ([`.github/workflows/ci.yml`](file:///home/lenovo/Documents/my_project/student_management_system/.github/workflows/ci.yml)):
    - **Job 1: `backend-tests`**: Runs on `ubuntu-latest` with PostgreSQL 16 and Redis 7 service containers, sets up Python 3.12, installs system libraries (`libpq-dev`, `gcc`), verifies Django settings, checks for unapplied/missing migrations (`makemigrations --check --dry-run`), and executes the complete 98-test backend suite.
    - **Job 2: `frontend-build`**: Sets up Bun runtime, installs node dependencies, compiles Svelte 5 production distribution, and verifies build artifacts (`dist/index.html`).
    - **Job 3: `docker-build-and-smoke`**: Validates `docker-compose.yml` configuration, builds container images, launches stack with detached mode, verifies healthcheck and port 80 accessibility via `curl`, smoke tests `/api/docs/` OpenAPI endpoint, and performs clean teardown.
  - [x] Added dynamic status badges in [`README.md`](file:///home/lenovo/Documents/my_project/student_management_system/README.md) for CI/CD workflow status, 100 passing tests, Python 3.12, Django 6.1, Svelte 5, and Docker stack.

---

### 14. One-Click Demo Database Seeder (SMS-19)
- **Objective**: Provide a single idempotent CLI management command (`python manage.py seed_demo_data`) and Docker boot integration (`SEED_DEMO_DATA=True`) to seed a complete realistic SMS environment with administrative, faculty, and student personas.
- **Tasks**:
  - [x] **RED Phase**: Authored test suite [`backend/student_management_app/tests/test_seeder.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/tests/test_seeder.py) verifying initial seed execution, entity existence, and idempotency across repeated executions.
  - [x] **GREEN Phase**: Implemented Django management command [`backend/student_management_app/management/commands/seed_demo_data.py`](file:///home/lenovo/Documents/my_project/student_management_system/backend/student_management_app/management/commands/seed_demo_data.py):
    - 2 Academic Sessions (`2025-2026`, `2026-2027`).
    - 3 Degree Programs (Computer Science & Engineering, Electrical & Electronic Engineering, Information Technology).
    - 1 Superuser Admin (`admin` / `admin123`).
    - 3 Faculty Staff Members with Base Salary & Allowances (`prof_smith`, `dr_johnson`, `lecturer_emily` / `staff123`).
    - 6 Course Subjects mapped to instructors.
    - 6 Enrolled Students across degree programs (`student_alex`, `student_bella`, `student_chris`, `student_david`, `student_eva`, `student_frank` / `student123`).
    - Multi-tier Fee Structures, Invoices (Paid, Partial, Unpaid), and Transaction Payment ledger.
    - Coursework Assignments and Student Submissions with Grading benchmarks.
    - Daily Subject Attendance records & reports.
    - Examination Marks, GPAs, and Letter Grades.
    - Monthly Faculty Payroll ledger with Paid/Pending records & PDF payslip targets.
    - In-app System Circulars and Broadcast Notifications.
  - [x] **Docker Integration**:
    - Updated [`backend/entrypoint.sh`](file:///home/lenovo/Documents/my_project/student_management_system/backend/entrypoint.sh) to execute `python manage.py seed_demo_data` on startup when `SEED_DEMO_DATA=True`.
    - Updated [`docker-compose.yml`](file:///home/lenovo/Documents/my_project/student_management_system/docker-compose.yml) and [`.env.docker.example`](file:///home/lenovo/Documents/my_project/student_management_system/.env.docker.example) with `SEED_DEMO_DATA=True`.
  - [x] **Verification**:
    - Full backend test suite passing: **100/100 tests OK (15 test modules)**.

---

## 🔮 Future Integration Roadmap

### Phase 15: Self-Service Password Reset (SMS-20)
- Tokenized self-service password reset flow with timed email tokens.










