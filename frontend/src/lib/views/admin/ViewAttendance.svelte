<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { ClipboardCheck, Search, CheckCircle, XCircle, AlertCircle, Loader2, FileDown } from 'lucide-svelte';

  let subjects = $state([]);
  let sessions = $state([]);
  let dates = $state([]);
  let studentReports = $state([]);

  let selectedSubject = $state('');
  let selectedSession = $state('');
  let selectedDateId = $state('');

  let loadingDates = $state(false);
  let loadingReports = $state(false);
  let exportingCsv = $state(false);
  let error = $state('');

  onMount(async () => {
    try {
      const [subs, sess] = await Promise.all([
        api.getSubjects(),
        api.getSessions()
      ]);
      subjects = subs;
      sessions = sess;
      if (subs.length > 0) selectedSubject = subs[0].id;
      if (sess.length > 0) selectedSession = sess[0].id;
    } catch (err) {
      error = err.message || 'Failed to load initial data';
    }
  });

  async function fetchDates() {
    if (!selectedSubject || !selectedSession) return;
    loadingDates = true;
    error = '';
    dates = [];
    studentReports = [];
    selectedDateId = '';
    try {
      dates = await api.getAttendanceDates(selectedSubject, selectedSession);
      if (dates.length > 0) {
        selectedDateId = dates[0].id;
        await fetchReports();
      }
    } catch (err) {
      error = err.message || 'Failed to load attendance dates';
    } finally {
      loadingDates = false;
    }
  }

  async function fetchReports() {
    if (!selectedDateId) return;
    loadingReports = true;
    error = '';
    try {
      studentReports = await api.getAttendanceReports(selectedDateId);
    } catch (err) {
      error = err.message || 'Failed to load attendance report';
    } finally {
      loadingReports = false;
    }
  }

  async function handleExportCsv() {
    exportingCsv = true;
    error = '';
    try {
      await api.exportAttendanceCsv({
        subject_id: selectedSubject,
        session_year_id: selectedSession
      });
    } catch (err) {
      error = err.message || 'Failed to export attendance CSV';
    } finally {
      exportingCsv = false;
    }
  }
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <ClipboardCheck class="text-blue-600" size={28} />
        View Student Attendance
      </h1>
      <p class="text-sm text-slate-500 mt-1">Audit daily student attendance logs by subject and session</p>
    </div>
    <button
      class="flex items-center gap-2 px-4 py-2.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-sm font-semibold shadow-sm transition-all self-start"
      onclick={handleExportCsv}
      disabled={exportingCsv}
    >
      {#if exportingCsv}
        <Loader2 size={16} class="animate-spin text-blue-600" />
        <span>Exporting...</span>
      {:else}
        <FileDown size={16} class="text-blue-600" />
        <span>Export Attendance CSV</span>
      {/if}
    </button>
  </div>

  {#if error}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-2 text-sm shadow-sm">
      <AlertCircle size={18} />
      <span>{error}</span>
    </div>
  {/if}

  <!-- Filters Card -->
  <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5" for="att-subj">Subject</label>
        <select id="att-subj" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20" bind:value={selectedSubject}>
          {#each subjects as s}
            <option value={s.id}>{s.subject_name} ({s.course_name})</option>
          {/each}
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5" for="att-sess">Session Year</label>
        <select id="att-sess" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20" bind:value={selectedSession}>
          {#each sessions as ses}
            <option value={ses.id}>{ses.session_start_year} TO {ses.session_end_year}</option>
          {/each}
        </select>
      </div>

      <div>
        <button
          class="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
          onclick={fetchDates}
          disabled={loadingDates || !selectedSubject || !selectedSession}
        >
          {#if loadingDates}
            <Loader2 size={16} class="animate-spin" />
            <span>Fetching...</span>
          {:else}
            <Search size={16} />
            <span>Fetch Dates</span>
          {/if}
        </button>
      </div>
    </div>
  </div>

  {#if dates.length > 0}
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3 max-w-md">
      <label class="text-xs font-semibold uppercase text-slate-600 whitespace-nowrap" for="att-date">Attendance Date:</label>
      <select id="att-date" class="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20" bind:value={selectedDateId} onchange={fetchReports}>
        {#each dates as d}
          <option value={d.id}>{d.attendance_date}</option>
        {/each}
      </select>
    </div>
  {/if}

  <!-- Attendance Log Table -->
  <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
    {#if loadingReports}
      <div class="p-12 text-center text-slate-400">
        <Loader2 size={32} class="animate-spin mx-auto mb-2 text-blue-500" />
        <p class="text-sm">Loading attendance records...</p>
      </div>
    {:else if studentReports.length > 0}
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-200/80 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-4">Student ID</th>
              <th class="py-3 px-4">Student Name</th>
              <th class="py-3 px-4 text-center">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            {#each studentReports as rep}
              <tr class="hover:bg-slate-50/60 transition-colors">
                <td class="py-3.5 px-4 font-mono text-xs text-slate-500">#{rep.id}</td>
                <td class="py-3.5 px-4 font-semibold text-slate-800">{rep.name}</td>
                <td class="py-3.5 px-4 text-center">
                  {#if rep.status}
                    <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                      <CheckCircle size={12} /> Present
                    </span>
                  {:else}
                    <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/60">
                      <XCircle size={12} /> Absent
                    </span>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else if dates.length > 0 && selectedDateId}
      <div class="p-12 text-center text-slate-400">
        <p class="text-sm font-medium">No student attendance records for this selected date.</p>
      </div>
    {/if}
  </div>
</div>

