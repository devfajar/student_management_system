<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { CheckCircle2, Search, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-svelte';

  let subjects = $state([]);
  let records = $state([]);
  let selectedSubject = $state('');
  let start_date = $state('');
  let end_date = $state('');

  let loading = $state(true);
  let searching = $state(false);
  let error = $state('');

  onMount(async () => {
    try {
      const [subs, recs] = await Promise.all([
        api.getSubjects(),
        api.studentViewAttendance()
      ]);
      subjects = subs;
      records = recs;
    } catch (err) {
      error = err.message || 'Failed to load attendance records';
    } finally {
      loading = false;
    }
  });

  async function handleFilter() {
    searching = true;
    error = '';
    try {
      records = await api.studentViewAttendance(selectedSubject, start_date, end_date);
    } catch (err) {
      error = err.message || 'Failed to filter attendance';
    } finally {
      searching = false;
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <CheckCircle2 size={20} color="#3b82f6" />
        My Attendance History
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
        <label class="form-label" for="stud-att-subj">Filter by Subject</label>
        <select id="stud-att-subj" class="form-control" bind:value={selectedSubject}>
          <option value="">All Subjects</option>
          {#each subjects as s}
            <option value={s.id}>{s.subject_name}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="stud-att-start">Start Date</label>
        <input id="stud-att-start" type="date" class="form-control" bind:value={start_date} />
      </div>

      <div class="form-group">
        <label class="form-label" for="stud-att-end">End Date</label>
        <input id="stud-att-end" type="date" class="form-control" bind:value={end_date} />
      </div>

      <div class="form-group filter-btn-group">
        <button class="btn btn-primary" onclick={handleFilter} disabled={searching}>
          <Search size={16} />
          <span>Apply Filter</span>
        </button>
      </div>
    </div>

    {#if loading || searching}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading attendance data...</p>
      </div>
    {:else if records.length === 0}
      <div class="empty-state">
        <p>No attendance records match your filter.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Subject</th>
              <th>Attendance Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {#each records as r}
              <tr>
                <td>#{r.id}</td>
                <td><strong>{r.subject_name}</strong></td>
                <td>{r.attendance_date}</td>
                <td>
                  {#if r.status}
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
    {/if}
  </div>
</div>

<style>
  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    align-items: flex-end;
    margin-bottom: 20px;
  }
  .filter-btn-group {
    display: flex;
    align-items: flex-end;
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
  }
</style>
