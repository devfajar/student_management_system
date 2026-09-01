<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import StatCard from '../../components/StatCard.svelte';
  import { Award, CheckCircle2, XCircle, BookOpen, Printer, AlertCircle, Loader2 } from 'lucide-svelte';

  let results = $state([]);
  let summary = $state({
    total_subjects: 0,
    passed_subjects: 0,
    failed_subjects: 0,
    average_score: 0
  });

  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      const data = await api.getStudentResults();
      results = data.results || [];
      summary = data.summary || summary;
    } catch (err) {
      error = err.message || 'Failed to load examination results';
    } finally {
      loading = false;
    }
  });

  function handlePrint() {
    window.print();
  }
</script>

<div class="content-body">
  <div class="page-header print-hidden">
    <div>
      <h2>Academic Transcript & Exam Results</h2>
      <p class="text-muted">Review your official examination scores, grades, and academic performance</p>
    </div>
    <button class="btn btn-outline" onclick={handlePrint}>
      <Printer size={16} />
      <span>Print Transcript</span>
    </button>
  </div>

  {#if loading}
    <div class="loading-state">
      <Loader2 size={32} class="animate-spin" color="#3b82f6" />
      <p>Loading your academic records...</p>
    </div>
  {:else if error}
    <div class="alert alert-danger">
      <AlertCircle size={16} />
      <span>{error}</span>
    </div>
  {:else}
    <!-- Summary Metrics -->
    <div class="stats-grid print-compact">
      <StatCard title="Average Score" value="{summary.average_score}%" color="blue">
        <Award size={24} />
      </StatCard>

      <StatCard title="Total Subjects" value={summary.total_subjects} color="purple">
        <BookOpen size={24} />
      </StatCard>

      <StatCard title="Subjects Passed" value={summary.passed_subjects} color="green">
        <CheckCircle2 size={24} />
      </StatCard>

      <StatCard title="Subjects Failed" value={summary.failed_subjects} color="red">
        <XCircle size={24} />
      </StatCard>
    </div>

    <!-- Results Table -->
    <div class="card transcript-card">
      <div class="card-header">
        <h3 class="card-title">
          <Award size={20} color="#3b82f6" />
          Course Subjects & Performance
        </h3>
      </div>

      {#if results.length === 0}
        <div class="empty-state">
          <p>No examination results published yet.</p>
        </div>
      {:else}
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Subject Name</th>
                <th>Course</th>
                <th>Assignment (50)</th>
                <th>Exam (50)</th>
                <th>Total (100)</th>
                <th>Grade</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {#each results as r, i}
                <tr>
                  <td>{i + 1}</td>
                  <td><strong>{r.subject_name}</strong></td>
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
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  .page-header h2 {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-main);
  }
  .text-muted {
    color: var(--text-muted);
    font-size: 13px;
    margin-top: 4px;
  }
  .btn-outline {
    background: white;
    border: 1px solid var(--border);
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-weight: 500;
  }
  .btn-outline:hover {
    background: #f8fafc;
    border-color: var(--primary);
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
  }

  @media print {
    .print-hidden {
      display: none !important;
    }
  }
</style>
