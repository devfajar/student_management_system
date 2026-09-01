<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { FileEdit, Search, Save, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let subjects = $state([]);
  let sessions = $state([]);
  let dates = $state([]);
  let studentReports = $state([]);

  let selectedSubject = $state('');
  let selectedSession = $state('');
  let selectedDateId = $state('');

  let loadingDates = $state(false);
  let loadingReports = $state(false);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

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
      error = err.message || 'Failed to load form data';
    }
  });

  async function fetchDates() {
    if (!selectedSubject || !selectedSession) return;
    loadingDates = true;
    error = '';
    success = '';
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
      error = err.message || 'Failed to fetch attendance dates';
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
      error = err.message || 'Failed to load attendance records';
    } finally {
      loadingReports = false;
    }
  }

  async function handleUpdateAttendance() {
    if (studentReports.length === 0) return;
    submitting = true;
    error = '';
    success = '';

    try {
      const payload = {
        student_data: studentReports.map(r => ({ id: r.id, status: r.status }))
      };
      await api.updateAttendance(payload);
      success = 'Attendance updated successfully!';
    } catch (err) {
      error = err.message || 'Failed to update attendance';
    } finally {
      submitting = false;
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <FileEdit size={20} color="#3b82f6" />
        Update Attendance
      </h2>
    </div>

    {#if success}
      <div class="alert alert-success">
        <CheckCircle size={16} />
        <span>{success}</span>
      </div>
    {/if}

    {#if error}
      <div class="alert alert-danger">
        <AlertCircle size={16} />
        <span>{error}</span>
      </div>
    {/if}

    <div class="filters-grid">
      <div class="form-group">
        <label class="form-label" for="up-subj">Subject</label>
        <select id="up-subj" class="form-control" bind:value={selectedSubject}>
          {#each subjects as s}
            <option value={s.id}>{s.subject_name} ({s.course_name})</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="up-sess">Session Year</label>
        <select id="up-sess" class="form-control" bind:value={selectedSession}>
          {#each sessions as ses}
            <option value={ses.id}>{ses.session_start_year} TO {ses.session_end_year}</option>
          {/each}
        </select>
      </div>

      <div class="form-group filter-btn-group">
        <button class="btn btn-primary" onclick={fetchDates} disabled={loadingDates}>
          <Search size={16} />
          <span>Fetch Attendance Dates</span>
        </button>
      </div>
    </div>

    {#if dates.length > 0}
      <div class="date-selector-group">
        <div class="form-group" style="max-width: 300px;">
          <label class="form-label" for="up-date">Select Attendance Date</label>
          <select id="up-date" class="form-control" bind:value={selectedDateId} onchange={fetchReports}>
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
        <p>Loading attendance data...</p>
      </div>
    {:else if studentReports.length > 0}
      <div class="table-container" style="margin-bottom: 20px;">
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
                  <label class="toggle-label">
                    <input type="checkbox" bind:checked={rep.status} />
                    <span class={rep.status ? 'status-present' : 'status-absent'}>
                      {rep.status ? 'Present' : 'Absent'}
                    </span>
                  </label>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <button class="btn btn-primary" onclick={handleUpdateAttendance} disabled={submitting}>
        {#if submitting}
          <Loader2 size={16} class="animate-spin" />
          <span>Updating...</span>
        {:else}
          <Save size={16} />
          <span>Save Changes</span>
        {/if}
      </button>
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
  .toggle-label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  .status-present {
    color: var(--success);
    font-weight: 600;
  }
  .status-absent {
    color: var(--danger);
    font-weight: 600;
  }
  .loading-state {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
  }
</style>
