<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import StatCard from '../../components/StatCard.svelte';
  import {
    Users, UserCheck, GraduationCap, BookOpen,
    Clock, UserPlus, BookPlus, PlusCircle, AlertCircle, Loader2
  } from 'lucide-svelte';

  let { currentView = $bindable() } = $props();

  let stats = $state(null);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      stats = await api.getDashboardStats();
    } catch (err) {
      error = err.message || 'Failed to load stats';
    } finally {
      loading = false;
    }
  });
</script>

<div class="content-body">
  <div class="page-header">
    <h2>Admin Dashboard</h2>
    <p class="text-muted">Overview of system metrics and quick management actions</p>
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
      <StatCard title="Total Students" value={stats?.student_count || 0} color="blue" onclick={() => currentView = 'manage-students'}>
        <Users size={24} />
      </StatCard>

      <StatCard title="Total Staff" value={stats?.staff_count || 0} color="green" onclick={() => currentView = 'manage-staff'}>
        <UserCheck size={24} />
      </StatCard>

      <StatCard title="Total Courses" value={stats?.course_count || 0} color="yellow" onclick={() => currentView = 'manage-courses'}>
        <GraduationCap size={24} />
      </StatCard>

      <StatCard title="Total Subjects" value={stats?.subject_count || 0} color="red" onclick={() => currentView = 'manage-subjects'}>
        <BookOpen size={24} />
      </StatCard>
    </div>

    {#if (stats?.pending_student_leaves || 0) > 0 || (stats?.pending_staff_leaves || 0) > 0}
      <div class="pending-banner">
        <Clock size={20} color="#f59e0b" />
        <div class="pending-text">
          <strong>Pending Actions:</strong>
          <span>{stats?.pending_student_leaves || 0} student leave requests, {stats?.pending_staff_leaves || 0} staff leave requests awaiting review.</span>
        </div>
      </div>
    {/if}

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Quick Actions</h3>
      </div>
      <div class="quick-grid">
        <button class="quick-action-btn" onclick={() => currentView = 'manage-students'}>
          <UserPlus size={24} color="#3b82f6" />
          <span>Manage Students</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'manage-staff'}>
          <UserCheck size={24} color="#10b981" />
          <span>Manage Staff</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'manage-courses'}>
          <BookPlus size={24} color="#f59e0b" />
          <span>Manage Courses</span>
        </button>
        <button class="quick-action-btn" onclick={() => currentView = 'manage-subjects'}>
          <PlusCircle size={24} color="#ef4444" />
          <span>Manage Subjects</span>
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
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 0;
    gap: 12px;
    color: var(--text-muted);
  }

  .pending-banner {
    background-color: var(--warning-light);
    border: 1px solid #fde68a;
    border-radius: var(--radius-md);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 24px;
    color: #92400e;
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
