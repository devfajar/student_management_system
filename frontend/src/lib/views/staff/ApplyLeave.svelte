<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Clock, Send, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let leaveHistory = $state([]);
  let leave_date = $state('');
  let leave_message = $state('');

  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

  async function loadLeaves() {
    loading = true;
    try {
      leaveHistory = await api.getStaffLeaves();
    } catch (err) {
      error = err.message || 'Failed to load leave history';
    } finally {
      loading = false;
    }
  }

  onMount(loadLeaves);

  async function handleApply(e) {
    e.preventDefault();
    submitting = true;
    error = '';
    success = '';

    try {
      await api.applyStaffLeave({ leave_date, leave_message });
      success = 'Leave request submitted successfully!';
      leave_date = '';
      leave_message = '';
      await loadLeaves();
    } catch (err) {
      error = err.message || 'Failed to submit leave request';
    } finally {
      submitting = false;
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <Clock size={20} color="#3b82f6" />
        Apply for Staff Leave
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

    <form onsubmit={handleApply} class="leave-form">
      <div class="form-group" style="max-width: 300px;">
        <label class="form-label" for="stf-leave-dt">Leave Date</label>
        <input id="stf-leave-dt" type="date" class="form-control" bind:value={leave_date} required />
      </div>

      <div class="form-group">
        <label class="form-label" for="stf-leave-msg">Reason for Leave</label>
        <textarea id="stf-leave-msg" class="form-control" bind:value={leave_message} placeholder="State reason for taking leave..." rows="3" required></textarea>
      </div>

      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={16} class="animate-spin" />
          <span>Submitting...</span>
        {:else}
          <Send size={16} />
          <span>Submit Leave Request</span>
        {/if}
      </button>
    </form>
  </div>

  <div class="card">
    <div class="card-header">
      <h3 class="card-title">Leave Request History</h3>
    </div>

    {#if loading}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading history...</p>
      </div>
    {:else if leaveHistory.length === 0}
      <div class="empty-state">
        <p>No leave requests found.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Leave Date</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Applied Date</th>
            </tr>
          </thead>
          <tbody>
            {#each leaveHistory as item}
              <tr>
                <td>#{item.id}</td>
                <td><span class="badge badge-info">{item.leave_date}</span></td>
                <td>{item.leave_message}</td>
                <td>
                  {#if item.leave_status === 1}
                    <span class="badge badge-success">Approved</span>
                  {:else if item.leave_status === 2}
                    <span class="badge badge-danger">Disapproved</span>
                  {:else}
                    <span class="badge badge-warning">Pending</span>
                  {/if}
                </td>
                <td>{new Date(item.created_at).toLocaleDateString()}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<style>
  .leave-form {
    margin-bottom: 8px;
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
  }
</style>
