<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import StatCard from '../../components/StatCard.svelte';
  import { CheckCircle2, XCircle, BookOpen, Clock, AlertCircle, Loader2 } from 'lucide-svelte';

  let { currentView = $bindable() } = $props();

  let stats = $state(null);
  let loading = $state(true);
  let error = $state('');

  const attendancePercent = $derived(
    stats?.total_attendance > 0
      ? Math.round((stats.attendance_present / stats.total_attendance) * 100)
      : 0
  );

  onMount(async () => {
    try {
      stats = await api.getDashboardStats();
    } catch (err) {
      error = err.message || 'Failed to load student metrics';
    } finally {
      loading = false;
    }
  });
</script>

<div class="content-body">
  <div class="page-header">
    <h2>Student Dashboard</h2>
    <p class="text-muted">Track your academic attendance records and requests</p>
  </div>

  {#if loading}
    <div class="loading-state">
      <Loader2 size={32} class="animate-spin" color="#3b82f6" />
      <p>Loading your data...</p>
    </div>
  {:else if error}
    <div class="alert alert-danger">
      <AlertCircle size={16} />
      <span>{error}</span>
    </div>
  {:else}
    <div class="stats-grid">
      <StatCard title="Total Classes" value={stats?.total_attendance || 0} color="blue" onclick={() => currentView = 'student-attendance'}>
        <CheckCircle2 size={24} />
      </StatCard>

      <StatCard title="Present Count" value={stats?.attendance_present || 0} color="green" onclick={() => currentView = 'student-attendance'}>
        <CheckCircle2 size={24} />
      </StatCard>

      <StatCard title="Absent Count" value={stats?.attendance_absent || 0} color="red" onclick={() => currentView = 'student-attendance'}>
        <XCircle size={24} />
      </StatCard>

      <StatCard title="Total Course Subjects" value={stats?.subjects_count || 0} color="purple">
        <BookOpen size={24} />
      </StatCard>
    </div>

    <!-- Attendance Percentage Card -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Overall Attendance Rate</h3>
      </div>
      <div class="attendance-progress-container">
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: {attendancePercent}%;"></div>
        </div>
        <div class="progress-info">
          <span>{attendancePercent}% Present</span>
          <span class="text-muted">({stats?.attendance_present || 0} of {stats?.total_attendance || 0} classes attended)</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Quick Actions</h3>
      </div>
      <div class="quick-grid">
        <button class="quick-action-btn" onclick={() => currentView = 'student-attendance'}>
          <CheckCircle2 size={24} color="#3b82f6" />
          <span>View Attendance History</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'student-apply-leave'}>
          <Clock size={24} color="#f59e0b" />
          <span>Apply for Leave</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'student-send-feedback'}>
          <BookOpen size={24} color="#10b981" />
          <span>Send Feedback</span>
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .page-header {
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
  .loading-state {
    text-align: center;
    padding: 60px 0;
    color: var(--text-muted);
  }

  .attendance-progress-container {
    padding: 8px 0;
  }

  .progress-bar-bg {
    height: 16px;
    background: #e2e8f0;
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 10px;
  }

  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #10b981);
    border-radius: 9999px;
    transition: width 0.4s ease;
  }

  .progress-info {
    display: flex;
    justify-content: space-between;
    font-weight: 600;
    font-size: 14px;
  }

  .quick-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }

  .quick-action-btn {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 20px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    cursor: pointer;
    transition: all 0.15s ease-in-out;
    font-weight: 500;
    color: var(--text-main);
  }

  .quick-action-btn:hover {
    background: #f8fafc;
    border-color: var(--primary);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
  }
</style>
