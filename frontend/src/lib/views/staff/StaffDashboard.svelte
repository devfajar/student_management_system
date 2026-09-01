<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import StatCard from '../../components/StatCard.svelte';
  import { Users, ClipboardCheck, BookOpen, Clock, AlertCircle, Loader2 } from 'lucide-svelte';

  let { currentView = $bindable() } = $props();

  let stats = $state(null);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      stats = await api.getDashboardStats();
    } catch (err) {
      error = err.message || 'Failed to load staff dashboard';
    } finally {
      loading = false;
    }
  });
</script>

<div class="content-body">
  <div class="page-header">
    <h2>Staff Dashboard</h2>
    <p class="text-muted">Welcome to your staff portal. Manage attendance and student interactions.</p>
  </div>

  {#if loading}
    <div class="loading-state">
      <Loader2 size={32} class="animate-spin" color="#3b82f6" />
      <p>Loading metrics...</p>
    </div>
  {:else if error}
    <div class="alert alert-danger">
      <AlertCircle size={16} />
      <span>{error}</span>
    </div>
  {:else}
    <div class="stats-grid">
      <StatCard title="Students Under Course" value={stats?.students_count || 0} color="blue" onclick={() => currentView = 'take-attendance'}>
        <Users size={24} />
      </StatCard>

      <StatCard title="Total Attendances Taken" value={stats?.attendance_count || 0} color="green" onclick={() => currentView = 'update-attendance'}>
        <ClipboardCheck size={24} />
      </StatCard>

      <StatCard title="Subjects Teaching" value={stats?.subject_count || 0} color="yellow">
        <BookOpen size={24} />
      </StatCard>

      <StatCard title="Approved Leaves" value={stats?.leave_count || 0} color="purple" onclick={() => currentView = 'apply-leave'}>
        <Clock size={24} />
      </StatCard>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Quick Actions</h3>
      </div>
      <div class="quick-grid">
        <button class="quick-action-btn" onclick={() => currentView = 'take-attendance'}>
          <ClipboardCheck size={24} color="#3b82f6" />
          <span>Take Attendance</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'update-attendance'}>
          <ClipboardCheck size={24} color="#10b981" />
          <span>Update Attendance</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'apply-leave'}>
          <Clock size={24} color="#f59e0b" />
          <span>Apply Leave</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'send-feedback'}>
          <BookOpen size={24} color="#8b5cf6" />
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
