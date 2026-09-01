<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Clock, CheckCircle2, XCircle, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let leaves = $state([]);
  let loading = $state(true);
  let error = $state('');
  let success = $state('');

  async function loadLeaves() {
    loading = true;
    try {
      leaves = await api.getStudentLeaves();
    } catch (err) {
      error = err.message || 'Failed to load leaves';
    } finally {
      loading = false;
    }
  }

  onMount(loadLeaves);

  async function handleApprove(id) {
    try {
      await api.approveStudentLeave(id);
      success = 'Leave request approved!';
      await loadLeaves();
    } catch (err) {
      error = err.message || 'Failed to approve leave';
    }
  }

  async function handleDisapprove(id) {
    try {
      await api.disapproveStudentLeave(id);
      success = 'Leave request disapproved!';
      await loadLeaves();
    } catch (err) {
      error = err.message || 'Failed to disapprove leave';
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <Clock size={20} color="#3b82f6" />
        Student Leave Requests
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

    {#if loading}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading leave requests...</p>
      </div>
    {:else if leaves.length === 0}
      <div class="empty-state">
        <p>No student leave requests found.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student Name</th>
              <th>Leave Date</th>
              <th>Message / Reason</th>
              <th>Status</th>
              <th>Applied Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {#each leaves as leave}
              <tr>
                <td>#{leave.id}</td>
                <td><strong>{leave.student_name}</strong></td>
                <td><span class="badge badge-info">{leave.leave_date}</span></td>
                <td>{leave.leave_message}</td>
                <td>
                  {#if leave.leave_status === 1}
                    <span class="badge badge-success">Approved</span>
                  {:else if leave.leave_status === 2}
                    <span class="badge badge-danger">Disapproved</span>
                  {:else}
                    <span class="badge badge-warning">Pending</span>
                  {/if}
                </td>
                <td>{new Date(leave.created_at).toLocaleDateString()}</td>
                <td>
                  {#if leave.leave_status === 0}
                    <div class="action-buttons">
                      <button class="btn btn-success btn-sm" onclick={() => handleApprove(leave.id)}>
                        <CheckCircle2 size={14} />
                        <span>Approve</span>
                      </button>
                      <button class="btn btn-danger btn-sm" onclick={() => handleDisapprove(leave.id)}>
                        <XCircle size={14} />
                        <span>Disapprove</span>
                      </button>
                    </div>
                  {:else}
                    <span class="text-muted">Reviewed</span>
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
  .action-buttons {
    display: flex;
    gap: 6px;
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
  }
</style>
