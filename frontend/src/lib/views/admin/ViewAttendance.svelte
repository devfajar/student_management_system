<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { ClipboardCheck, Search, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-svelte';

  let subjects = $state([]);
  let sessions = $state([]);
  let dates = $state([]);
  let studentReports = $state([]);

  let selectedSubject = $state('');
  let selectedSession = $state('');
  let selectedDateId = $state('');

  let loadingDates = $state(false);
  let loadingReports = $state(false);
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
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <ClipboardCheck size={20} color="#3b82f6" />
        View Student Attendance
      </h2>
    </div>

    {#if error}
      <div class="alert alert-danger">
        <AlertCircle size={16} />
        <span>{error}</span>
      </div>
    {/if}

    <div class="filters-grid">
      <div class="form-group">
        <label class="form-label" for="att-subj">Select Subject</label>
        <select id="att-subj" class="form-control" bind:value={selectedSubject}>
          {#each subjects as s}
            <option value={s.id}>{s.subject_name} ({s.course_name})</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="att-sess">Select Session Year</label>
        <select id="att-sess" class="form-control" bind:value={selectedSession}>
          {#each sessions as ses}
            <option value={ses.id}>{ses.session_start_year} TO {ses.session_end_year}</option>
          {/each}
        </select>
      </div>

      <div class="form-group filter-btn-group">
        <button class="btn btn-primary" onclick={fetchDates} disabled={loadingDates || !selectedSubject || !selectedSession}>
          <Search size={16} />
          <span>Fetch Dates</span>
        </button>
      </div>
    </div>

    {#if dates.length > 0}
      <div class="date-selector-group">
        <div class="form-group" style="max-width: 320px;">
          <label class="form-label" for="att-date">Attendance Date</label>
          <select id="att-date" class="form-control" bind:value={selectedDateId} onchange={fetchReports}>
            {#each dates as d}
              <option value={d.id}>{d.attendance_date}</option>
            {/each}
          </select>
        </div>
      </div>
    {/if}

    {#if loadingReports}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading attendance details...</p>
      </div>
    {:else if studentReports.length > 0}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student Name</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {#each studentReports as rep}
              <tr>
                <td>#{rep.id}</td>
                <td><strong>{rep.name}</strong></td>
                <td>
                  {#if rep.status}
                    <span class="badge badge-success">
                      <CheckCircle size={12} style="margin-right: 4px;" /> Present
                    </span>
                  {:else}
                    <span class="badge badge-danger">
                      <XCircle size={12} style="margin-right: 4px;" /> Absent
                    </span>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else if dates.length > 0 && selectedDateId}
      <div class="empty-state">
        <p>No student attendance records for this date.</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    align-items: flex-end;
    margin-bottom: 20px;
  }
  .filter-btn-group {
    display: flex;
    align-items: flex-end;
  }
  .date-selector-group {
    padding: 16px;
    background: #f8fafc;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    margin-bottom: 20px;
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
  }
</style>
