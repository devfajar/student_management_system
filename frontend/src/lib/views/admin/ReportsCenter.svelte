<script>
  import { onMount } from 'svelte';
  import { api } from '../../api';
  import {
    FileSpreadsheet,
    FileText,
    FileDown,
    Search,
    RefreshCw,
    Users,
    ClipboardCheck,
    CreditCard,
    Award,
    ChevronLeft,
    ChevronRight,
    Download,
    CheckCircle2,
    XCircle,
    AlertCircle
  } from 'lucide-svelte';

  // State
  let activeTab = $state('students'); // 'students', 'attendance', 'fees', 'results'
  let searchQuery = $state('');
  let selectedCourse = $state('');
  let selectedSubject = $state('');
  let selectedSession = $state('');
  let selectedStatus = $state('');
  let startDate = $state('');
  let endDate = $state('');

  // Pagination
  let currentPage = $state(1);
  let pageSize = $state(10);
  let totalCount = $state(0);
  let totalPages = $state(1);

  // Data & Loading
  let records = $state([]);
  let loading = $state(false);
  let exporting = $state(false);
  let errorMessage = $state('');
  let successMessage = $state('');

  // Dropdown reference data
  let courses = $state([]);
  let subjects = $state([]);
  let sessions = $state([]);

  let searchDebounceTimer;

  onMount(async () => {
    await loadReferenceData();
    await fetchReports();
  });

  async function loadReferenceData() {
    try {
      const [c, s, sess] = await Promise.all([
        api.getCourses().catch(() => []),
        api.getSubjects().catch(() => []),
        api.getSessions().catch(() => [])
      ]);
      courses = c || [];
      subjects = s || [];
      sessions = sess || [];
    } catch (err) {
      console.error('Error loading reference data', err);
    }
  }

  async function fetchReports() {
    loading = true;
    errorMessage = '';
    try {
      const params = {
        type: activeTab,
        page: currentPage,
        page_size: pageSize
      };
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (selectedCourse) params.course_id = selectedCourse;
      if (selectedSubject) params.subject_id = selectedSubject;
      if (selectedSession) params.session_year_id = selectedSession;
      if (selectedStatus) params.status = selectedStatus;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const res = await api.getReportsPreview(params);
      records = res.results || [];
      totalCount = res.count || 0;
      totalPages = res.total_pages || 1;
      currentPage = res.current_page || 1;
    } catch (err) {
      errorMessage = err.message || 'Failed to load report data';
      records = [];
    } finally {
      loading = false;
    }
  }

  function handleSearchInput() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      currentPage = 1;
      fetchReports();
    }, 350);
  }

  function handleTabChange(tab) {
    activeTab = tab;
    currentPage = 1;
    searchQuery = '';
    selectedStatus = '';
    fetchReports();
  }

  function handleFilterChange() {
    currentPage = 1;
    fetchReports();
  }

  function resetFilters() {
    searchQuery = '';
    selectedCourse = '';
    selectedSubject = '';
    selectedSession = '';
    selectedStatus = '';
    startDate = '';
    endDate = '';
    currentPage = 1;
    fetchReports();
  }

  function changePage(newPage) {
    if (newPage >= 1 && newPage <= totalPages) {
      currentPage = newPage;
      fetchReports();
    }
  }

  // Export handlers
  async function handleExportExcel() {
    exporting = true;
    errorMessage = '';
    try {
      const params = {};
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (selectedCourse) params.course_id = selectedCourse;
      if (selectedSubject) params.subject_id = selectedSubject;
      if (selectedSession) params.session_year_id = selectedSession;
      if (selectedStatus) params.status = selectedStatus;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      if (activeTab === 'students') {
        await api.exportStudentsExcel(params);
      } else if (activeTab === 'attendance') {
        await api.exportAttendanceExcel(params);
      } else if (activeTab === 'fees') {
        await api.exportFeesExcel(params);
      } else if (activeTab === 'results') {
        await api.exportResultsExcel(params);
      }
      showFlash('Excel workbook exported successfully!');
    } catch (err) {
      errorMessage = err.message || 'Failed to export Excel file';
    } finally {
      exporting = false;
    }
  }

  async function handleExportCsv() {
    exporting = true;
    errorMessage = '';
    try {
      const params = {};
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (selectedCourse) params.course_id = selectedCourse;
      if (selectedSubject) params.subject_id = selectedSubject;
      if (selectedSession) params.session_year_id = selectedSession;
      if (selectedStatus) params.status = selectedStatus;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      if (activeTab === 'students') {
        await api.exportStudentsCsv(params);
      } else if (activeTab === 'attendance') {
        await api.exportAttendanceCsv(params);
      } else if (activeTab === 'fees') {
        await api.exportFeesCsv(params);
      } else if (activeTab === 'results') {
        await api.exportResultsCsv(params);
      }
      showFlash('CSV file exported successfully!');
    } catch (err) {
      errorMessage = err.message || 'Failed to export CSV file';
    } finally {
      exporting = false;
    }
  }

  async function handleDownloadStudentPdf(studentId) {
    try {
      await api.exportReportCardPdf(studentId);
      showFlash('Report Card PDF downloaded!');
    } catch (err) {
      errorMessage = err.message || 'Failed to download report card';
    }
  }

  function showFlash(msg) {
    successMessage = msg;
    setTimeout(() => {
      successMessage = '';
    }, 4000);
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div>
      <div class="flex items-center gap-2 text-sm font-semibold text-blue-600 uppercase tracking-wider">
        <FileSpreadsheet size={16} />
        <span>Institutional Intelligence</span>
      </div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight">Reports & Export Hub</h1>
      <p class="text-sm text-slate-500 mt-0.5">Generate and download official PDF, Excel (.xlsx), and CSV files with server-side pagination & live search.</p>
    </div>

    <!-- Export Action Buttons -->
    <div class="flex flex-wrap items-center gap-2">
      <button
        onclick={handleExportExcel}
        disabled={exporting || loading}
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition-all active:scale-95 disabled:opacity-50"
      >
        <FileSpreadsheet size={16} />
        <span>{exporting ? 'Exporting...' : 'Export Excel (.xlsx)'}</span>
      </button>

      <button
        onclick={handleExportCsv}
        disabled={exporting || loading}
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-all active:scale-95 disabled:opacity-50"
      >
        <FileText size={16} />
        <span>{exporting ? 'Exporting...' : 'Export CSV (.csv)'}</span>
      </button>

      {#if activeTab === 'students'}
        <button
          onclick={() => handleDownloadStudentPdf(null)}
          disabled={exporting || loading}
          class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          title="Download sample student report card"
        >
          <FileDown size={16} />
          <span>Report Card PDF</span>
        </button>
      {/if}
    </div>
  </div>

  <!-- Notification alerts -->
  {#if successMessage}
    <div class="flex items-center gap-3 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium animate-fadeIn">
      <CheckCircle2 size={16} class="text-emerald-600 shrink-0" />
      <span>{successMessage}</span>
    </div>
  {/if}

  {#if errorMessage}
    <div class="flex items-center gap-3 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium animate-fadeIn">
      <AlertCircle size={16} class="text-rose-600 shrink-0" />
      <span>{errorMessage}</span>
    </div>
  {/if}

  <!-- Report Navigation Tabs -->
  <div class="flex flex-wrap items-center gap-2 p-1.5 bg-slate-100/80 rounded-2xl border border-slate-200/80">
    <button
      onclick={() => handleTabChange('students')}
      class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all {activeTab === 'students' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}"
    >
      <Users size={16} />
      <span>Student Roster</span>
    </button>

    <button
      onclick={() => handleTabChange('attendance')}
      class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all {activeTab === 'attendance' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}"
    >
      <ClipboardCheck size={16} />
      <span>Attendance Logs</span>
    </button>

    <button
      onclick={() => handleTabChange('fees')}
      class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all {activeTab === 'fees' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}"
    >
      <CreditCard size={16} />
      <span>Fee Ledger</span>
    </button>

    <button
      onclick={() => handleTabChange('results')}
      class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all {activeTab === 'results' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}"
    >
      <Award size={16} />
      <span>Exam Results</span>
    </button>
  </div>

  <!-- Search & Filter Controls Card -->
  <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <!-- Search Input -->
      <div class="relative sm:col-span-2">
        <Search size={16} class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          bind:value={searchQuery}
          oninput={handleSearchInput}
          placeholder="Search by student name, username, subject, or invoice..."
          class="w-full pl-10 pr-4 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all placeholder:text-slate-400"
        />
      </div>

      <!-- Course Filter -->
      <div>
        <select
          bind:value={selectedCourse}
          onchange={handleFilterChange}
          class="w-full px-3 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        >
          <option value="">All Courses</option>
          {#each courses as c}
            <option value={c.id}>{c.course_name}</option>
          {/each}
        </select>
      </div>

      <!-- Subject Filter (for attendance & results) -->
      {#if activeTab === 'attendance' || activeTab === 'results'}
        <div>
          <select
            bind:value={selectedSubject}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            <option value="">All Subjects</option>
            {#each subjects as s}
              <option value={s.id}>{s.subject_name}</option>
            {/each}
          </select>
        </div>
      {:else}
        <!-- Session Filter (for students & fees) -->
        <div>
          <select
            bind:value={selectedSession}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            <option value="">All Academic Sessions</option>
            {#each sessions as sess}
              <option value={sess.id}>{sess.session_start_year} - {sess.session_end_year}</option>
            {/each}
          </select>
        </div>
      {/if}
    </div>

    <!-- Second Row Filters: Status & Date Ranges -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1 border-t border-slate-100">
      <!-- Status Filter -->
      {#if activeTab === 'fees'}
        <div>
          <select
            bind:value={selectedStatus}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            <option value="">All Payment Statuses</option>
            <option value="Paid">Paid (Full)</option>
            <option value="Partial">Partial</option>
            <option value="Unpaid">Unpaid</option>
          </select>
        </div>
      {:else if activeTab === 'attendance'}
        <div>
          <select
            bind:value={selectedStatus}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="Present">Present</option>
            <option value="Absent">Absent</option>
          </select>
        </div>
      {/if}

      <!-- Date Filters (Attendance) -->
      {#if activeTab === 'attendance'}
        <div>
          <input
            type="date"
            bind:value={startDate}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
            placeholder="From Date"
          />
        </div>
        <div>
          <input
            type="date"
            bind:value={endDate}
            onchange={handleFilterChange}
            class="w-full px-3 py-2 rounded-xl text-xs bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
            placeholder="To Date"
          />
        </div>
      {/if}

      <div class="flex items-center gap-2">
        <button
          onclick={resetFilters}
          class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-all"
        >
          Reset Filters
        </button>
        <button
          onclick={fetchReports}
          class="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-all"
          title="Refresh Data"
        >
          <RefreshCw size={15} class={loading ? 'animate-spin' : ''} />
        </button>
      </div>
    </div>
  </div>

  <!-- Paginated Data Table Card -->
  <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
    {#if loading}
      <div class="flex flex-col items-center justify-center p-16 text-slate-400 space-y-3">
        <RefreshCw size={28} class="animate-spin text-blue-600" />
        <p class="text-xs font-medium">Fetching real-time records...</p>
      </div>
    {:else if records.length === 0}
      <div class="flex flex-col items-center justify-center p-16 text-slate-400 space-y-3">
        <AlertCircle size={32} class="text-slate-300" />
        <p class="text-xs font-medium">No records match the current filter or search criteria.</p>
        <button onclick={resetFilters} class="text-xs text-blue-600 font-semibold hover:underline">
          Clear all filters
        </button>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/80 border-b border-slate-200/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              {#if activeTab === 'students'}
                <th class="py-3.5 px-4">ID</th>
                <th class="py-3.5 px-4">Student</th>
                <th class="py-3.5 px-4">Email</th>
                <th class="py-3.5 px-4">Course</th>
                <th class="py-3.5 px-4">Session</th>
                <th class="py-3.5 px-4">Gender</th>
                <th class="py-3.5 px-4 text-right">Actions</th>
              {:else if activeTab === 'attendance'}
                <th class="py-3.5 px-4">ID</th>
                <th class="py-3.5 px-4">Student</th>
                <th class="py-3.5 px-4">Subject</th>
                <th class="py-3.5 px-4">Attendance Date</th>
                <th class="py-3.5 px-4">Status</th>
              {:else if activeTab === 'fees'}
                <th class="py-3.5 px-4">Invoice #</th>
                <th class="py-3.5 px-4">Student</th>
                <th class="py-3.5 px-4">Course</th>
                <th class="py-3.5 px-4">Fee Structure</th>
                <th class="py-3.5 px-4">Total</th>
                <th class="py-3.5 px-4">Paid</th>
                <th class="py-3.5 px-4">Balance</th>
                <th class="py-3.5 px-4">Status</th>
              {:else if activeTab === 'results'}
                <th class="py-3.5 px-4">ID</th>
                <th class="py-3.5 px-4">Student</th>
                <th class="py-3.5 px-4">Course</th>
                <th class="py-3.5 px-4">Subject</th>
                <th class="py-3.5 px-4">Exam Marks</th>
                <th class="py-3.5 px-4">Assignment</th>
                <th class="py-3.5 px-4">Total Score</th>
                <th class="py-3.5 px-4">Grade</th>
                <th class="py-3.5 px-4">Status</th>
              {/if}
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-xs text-slate-700">
            {#each records as row}
              <tr class="hover:bg-slate-50/60 transition-colors">
                {#if activeTab === 'students'}
                  <td class="py-3 px-4 font-mono text-slate-500">#{row.id}</td>
                  <td class="py-3 px-4">
                    <div class="font-semibold text-slate-800">{row.full_name || row.username}</div>
                    <div class="text-[11px] text-slate-400">@{row.username}</div>
                  </td>
                  <td class="py-3 px-4 text-slate-600">{row.email || '—'}</td>
                  <td class="py-3 px-4 font-medium text-slate-700">{row.course_name || '—'}</td>
                  <td class="py-3 px-4 text-slate-500">{row.session_year || '—'}</td>
                  <td class="py-3 px-4 text-slate-600">{row.gender || '—'}</td>
                  <td class="py-3 px-4 text-right">
                    <button
                      onclick={() => handleDownloadStudentPdf(row.id)}
                      class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold text-[11px] transition-all"
                      title="Download Academic Transcript / Report Card"
                    >
                      <Download size={13} />
                      <span>Transcript</span>
                    </button>
                  </td>

                {:else if activeTab === 'attendance'}
                  <td class="py-3 px-4 font-mono text-slate-500">#{row.id}</td>
                  <td class="py-3 px-4">
                    <div class="font-semibold text-slate-800">{row.full_name || row.username}</div>
                    <div class="text-[11px] text-slate-400">@{row.username}</div>
                  </td>
                  <td class="py-3 px-4 font-medium text-slate-700">{row.subject_name}</td>
                  <td class="py-3 px-4 font-mono text-slate-600">{row.attendance_date}</td>
                  <td class="py-3 px-4">
                    {#if row.status}
                      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 size={12} /> Present
                      </span>
                    {:else}
                      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                        <XCircle size={12} /> Absent
                      </span>
                    {/if}
                  </td>

                {:else if activeTab === 'fees'}
                  <td class="py-3 px-4 font-mono text-blue-600 font-semibold">INV-{row.id}</td>
                  <td class="py-3 px-4">
                    <div class="font-semibold text-slate-800">{row.full_name || row.username}</div>
                    <div class="text-[11px] text-slate-400">@{row.username}</div>
                  </td>
                  <td class="py-3 px-4 text-slate-600">{row.course_name}</td>
                  <td class="py-3 px-4 font-medium text-slate-700">{row.fee_name}</td>
                  <td class="py-3 px-4 font-mono font-semibold text-slate-800">${row.total_amount?.toFixed(2)}</td>
                  <td class="py-3 px-4 font-mono text-emerald-600 font-semibold">${row.paid_amount?.toFixed(2)}</td>
                  <td class="py-3 px-4 font-mono text-rose-600 font-semibold">${row.balance_amount?.toFixed(2)}</td>
                  <td class="py-3 px-4">
                    {#if row.payment_status?.toUpperCase() === 'PAID'}
                      <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Paid</span>
                    {:else if row.payment_status?.toUpperCase() === 'PARTIAL'}
                      <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">Partial</span>
                    {:else}
                      <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">Unpaid</span>
                    {/if}
                  </td>

                {:else if activeTab === 'results'}
                  <td class="py-3 px-4 font-mono text-slate-500">#{row.id}</td>
                  <td class="py-3 px-4">
                    <div class="font-semibold text-slate-800">{row.full_name || row.username}</div>
                    <div class="text-[11px] text-slate-400">@{row.username}</div>
                  </td>
                  <td class="py-3 px-4 text-slate-600">{row.course_name}</td>
                  <td class="py-3 px-4 font-medium text-slate-700">{row.subject_name}</td>
                  <td class="py-3 px-4 font-mono text-slate-700">{row.exam_marks}</td>
                  <td class="py-3 px-4 font-mono text-slate-700">{row.assignment_marks}</td>
                  <td class="py-3 px-4 font-mono font-bold text-slate-900">{row.total_marks}</td>
                  <td class="py-3 px-4">
                    <span class="px-2 py-0.5 rounded font-bold text-xs bg-blue-50 text-blue-700 border border-blue-200">
                      {row.grade}
                    </span>
                  </td>
                  <td class="py-3 px-4">
                    {#if row.status === 'Pass'}
                      <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Pass</span>
                    {:else}
                      <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">Fail</span>
                    {/if}
                  </td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <!-- Pagination Bar -->
      <div class="p-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div class="flex items-center gap-2">
          <span>Showing</span>
          <span class="font-semibold text-slate-800">
            {totalCount === 0 ? 0 : (currentPage - 1) * pageSize + 1}
          </span>
          <span>to</span>
          <span class="font-semibold text-slate-800">
            {Math.min(currentPage * pageSize, totalCount)}
          </span>
          <span>of</span>
          <span class="font-semibold text-slate-800">{totalCount}</span>
          <span>entries</span>

          <span class="mx-2 text-slate-300">|</span>

          <span>Rows per page:</span>
          <select
            bind:value={pageSize}
            onchange={() => { currentPage = 1; fetchReports(); }}
            class="px-2 py-1 rounded-lg border border-slate-200 bg-slate-50 font-medium text-slate-700 focus:outline-none"
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>

        <!-- Page Navigator Buttons -->
        <div class="flex items-center gap-1.5">
          <button
            onclick={() => changePage(currentPage - 1)}
            disabled={currentPage <= 1 || loading}
            class="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            title="Previous Page"
          >
            <ChevronLeft size={16} />
          </button>

          <span class="px-3 py-1 text-xs font-semibold text-slate-700">
            Page {currentPage} of {totalPages}
          </span>

          <button
            onclick={() => changePage(currentPage + 1)}
            disabled={currentPage >= totalPages || loading}
            class="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            title="Next Page"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>
