<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Award, Trash2, Search, Filter, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let results = $state([]);
  let courses = $state([]);
  let subjects = $state([]);

  let selectedCourse = $state('');
  let selectedSubject = $state('');
  let searchQuery = $state('');

  let loading = $state(true);
  let error = $state('');
  let success = $state('');

  async function loadData() {
    loading = true;
    error = '';
    try {
      const [crs, subs, res] = await Promise.all([
        api.getCourses(),
        api.getSubjects(),
        api.getResults({
          course_id: selectedCourse,
          subject_id: selectedSubject
        })
      ]);
      courses = crs;
      subjects = subs;
      results = res;
    } catch (err) {
      error = err.message || 'Failed to load examination records';
    } finally {
      loading = false;
    }
  }

  onMount(loadData);

  async function handleFilter() {
    loading = true;
    error = '';
    try {
      results = await api.getResults({
        course_id: selectedCourse,
        subject_id: selectedSubject
      });
    } catch (err) {
      error = err.message || 'Failed to filter records';
    } finally {
      loading = false;
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to remove this student examination record?')) return;
    try {
      await api.deleteResult(id);
      success = 'Examination record deleted successfully.';
      await handleFilter();
    } catch (err) {
      error = err.message || 'Failed to delete record';
    }
  }

  const filteredResults = $derived(
    results.filter(r => {
      const q = searchQuery.toLowerCase();
      return (
        r.student_name.toLowerCase().includes(q) ||
        r.student_username.toLowerCase().includes(q) ||
        r.subject_name.toLowerCase().includes(q)
      );
    })
  );
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <Award size={20} color="#3b82f6" />
        Examination Results & Grades Ledger
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
        <label class="form-label" for="adm-res-crs">Filter by Course</label>
        <select id="adm-res-crs" class="form-control" bind:value={selectedCourse} onchange={handleFilter}>
          <option value="">All Courses</option>
          {#each courses as c}
            <option value={c.id}>{c.course_name}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="adm-res-sub">Filter by Subject</label>
        <select id="adm-res-sub" class="form-control" bind:value={selectedSubject} onchange={handleFilter}>
          <option value="">All Subjects</option>
          {#each subjects as s}
            <option value={s.id}>{s.subject_name} ({s.course_name})</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="adm-res-search">Search Student</label>
        <div class="search-input-wrapper">
          <Search size={16} class="search-icon" />
          <input
            id="adm-res-search"
            type="text"
            class="form-control with-icon"
            placeholder="Search by student name or username..."
            bind:value={searchQuery}
          />
        </div>
      </div>
    </div>

    {#if loading}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading results ledger...</p>
      </div>
    {:else if filteredResults.length === 0}
      <div class="empty-state">
        <p>No examination results found matching current criteria.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student Name</th>
              <th>Username</th>
              <th>Subject</th>
              <th>Course</th>
              <th>Assignment</th>
              <th>Exam</th>
              <th>Total Marks</th>
              <th>Grade</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredResults as r}
              <tr>
                <td>#{r.id}</td>
                <td><strong>{r.student_name}</strong></td>
                <td><code>{r.student_username}</code></td>
                <td>{r.subject_name}</td>
                <td><span class="badge badge-info">{r.course_name}</span></td>
                <td>{r.subject_assignment_marks}</td>
                <td>{r.subject_exam_marks}</td>
                <td><strong>{r.total_marks} / 100</strong></td>
                <td>
                  {#if r.grade === 'A+' || r.grade === 'A'}
                    <span class="badge badge-success">{r.grade}</span>
                  {:else if r.grade === 'B'}
                    <span class="badge badge-info">{r.grade}</span>
                  {:else if r.grade === 'C' || r.grade === 'D'}
                    <span class="badge badge-warning">{r.grade}</span>
                  {:else}
                    <span class="badge badge-danger">{r.grade}</span>
                  {/if}
                </td>
                <td>
                  {#if r.status === 'Passed'}
                    <span class="badge badge-success">Passed</span>
                  {:else}
                    <span class="badge badge-danger">Failed</span>
                  {/if}
                </td>
                <td>
                  <button class="btn btn-danger btn-sm" onclick={() => handleDelete(r.id)} aria-label="Delete Record">
                    <Trash2 size={14} />
                  </button>
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
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
  }
  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }
  .search-icon {
    position: absolute;
    left: 10px;
    color: var(--text-muted);
  }
  .with-icon {
    padding-left: 32px;
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
  }
</style>
