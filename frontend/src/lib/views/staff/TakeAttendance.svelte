<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { ClipboardCheck, Search, Save, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let subjects = $state([]);
  let sessions = $state([]);
  let students = $state([]);

  let selectedSubject = $state('');
  let selectedSession = $state('');
  let attendance_date = $state(new Date().toISOString().split('T')[0]);

  let loadingStudents = $state(false);
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
      error = err.message || 'Failed to load initial form data';
    }
  });

  async function fetchStudents() {
    if (!selectedSubject || !selectedSession) return;
    loadingStudents = true;
    error = '';
    success = '';
    students = [];
    try {
      const res = await api.getAttendanceStudents(selectedSubject, selectedSession);
      students = res.map(s => ({ ...s, status: true })); // default present
    } catch (err) {
      error = err.message || 'Failed to fetch students for this subject and session';
    } finally {
      loadingStudents = false;
    }
  }

  async function handleSaveAttendance() {
    if (students.length === 0) return;
    submitting = true;
    error = '';
    success = '';

    try {
      const payload = {
        subject_id: selectedSubject,
        session_year_id: selectedSession,
        attendance_date,
        student_ids: students.map(s => ({ id: s.id, status: s.status }))
      };
      await api.saveAttendance(payload);
      success = 'Attendance saved successfully!';
      students = [];
    } catch (err) {
      error = err.message || 'Failed to save attendance';
    } finally {
      submitting = false;
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <ClipboardCheck size={20} color="#3b82f6" />
        Take Attendance
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
        <label class="form-label" for="staff-att-subj">Subject</label>
        <select id="staff-att-subj" class="form-control" bind:value={selectedSubject}>
          {#each subjects as s}
            <option value={s.id}>{s.subject_name} ({s.course_name})</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="staff-att-sess">Session Year</label>
        <select id="staff-att-sess" class="form-control" bind:value={selectedSession}>
          {#each sessions as ses}
            <option value={ses.id}>{ses.session_start_year} TO {ses.session_end_year}</option>
          {/each}
        </select>
      </div>

      <div class="form-group filter-btn-group">
        <button class="btn btn-primary" onclick={fetchStudents} disabled={loadingStudents}>
          <Search size={16} />
          <span>Fetch Students</span>
        </button>
      </div>
    </div>

    {#if loadingStudents}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Fetching enrolled students...</p>
      </div>
    {:else if students.length > 0}
      <div class="attendance-sheet">
        <div class="form-group" style="max-width: 250px; margin-bottom: 20px;">
          <label class="form-label" for="staff-att-date">Attendance Date</label>
          <input id="staff-att-date" type="date" class="form-control" bind:value={attendance_date} required />
        </div>

        <div class="table-container" style="margin-bottom: 20px;">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Student Name</th>
                <th>Email</th>
                <th>Present / Absent</th>
              </tr>
            </thead>
            <tbody>
              {#each students as s}
                <tr>
                  <td>#{s.id}</td>
                  <td><strong>{s.name}</strong></td>
                  <td>{s.email}</td>
                  <td>
                    <label class="toggle-label">
                      <input type="checkbox" bind:checked={s.status} />
                      <span class={s.status ? 'status-present' : 'status-absent'}>
                        {s.status ? 'Present' : 'Absent'}
                      </span>
                    </label>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <button class="btn btn-success" onclick={handleSaveAttendance} disabled={submitting}>
          {#if submitting}
            <Loader2 size={16} class="animate-spin" />
            <span>Saving Attendance...</span>
          {:else}
            <Save size={16} />
            <span>Submit Attendance</span>
          {/if}
        </button>
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
  .attendance-sheet {
    padding-top: 16px;
    border-top: 1px solid var(--border);
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
