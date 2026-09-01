<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import { MessageSquare, Reply, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let feedbacks = $state([]);
  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

  // Modal
  let showModal = $state(false);
  let activeFeedback = $state(null);
  let reply_message = $state('');

  async function loadFeedback() {
    loading = true;
    try {
      feedbacks = await api.getStaffFeedback();
    } catch (err) {
      error = err.message || 'Failed to load staff feedback';
    } finally {
      loading = false;
    }
  }

  onMount(loadFeedback);

  function openReplyModal(fb) {
    activeFeedback = fb;
    reply_message = fb.feedback_reply || '';
    showModal = true;
  }

  async function handleSendReply(e) {
    e.preventDefault();
    if (!activeFeedback) return;
    submitting = true;
    error = '';
    try {
      await api.replyStaffFeedback(activeFeedback.id, reply_message);
      success = 'Reply sent successfully!';
      showModal = false;
      await loadFeedback();
    } catch (err) {
      error = err.message || 'Failed to send reply';
    } finally {
      submitting = false;
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <MessageSquare size={20} color="#3b82f6" />
        Staff Feedback
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
        <p>Loading feedback...</p>
      </div>
    {:else if feedbacks.length === 0}
      <div class="empty-state">
        <p>No staff feedback received yet.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Staff Name</th>
              <th>Feedback Message</th>
              <th>Sent Date</th>
              <th>Reply</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {#each feedbacks as fb}
              <tr>
                <td>#{fb.id}</td>
                <td><strong>{fb.staff_name}</strong></td>
                <td>{fb.feedback}</td>
                <td>{new Date(fb.created_at).toLocaleDateString()}</td>
                <td>
                  {#if fb.feedback_reply}
                    <span class="reply-text">{fb.feedback_reply}</span>
                  {:else}
                    <span class="badge badge-warning">No reply yet</span>
                  {/if}
                </td>
                <td>
                  <button class="btn btn-outline btn-sm" onclick={() => openReplyModal(fb)}>
                    <Reply size={14} />
                    <span>{fb.feedback_reply ? 'Edit Reply' : 'Reply'}</span>
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

<Modal show={showModal} title="Reply to Staff Feedback" onclose={() => showModal = false}>
  <form onsubmit={handleSendReply}>
    <div class="feedback-context">
      <p><strong>Staff:</strong> {activeFeedback?.staff_name}</p>
      <p><strong>Message:</strong> {activeFeedback?.feedback}</p>
    </div>

    <div class="form-group">
      <label class="form-label" for="fb-staff-reply">Your Reply</label>
      <textarea id="fb-staff-reply" class="form-control" bind:value={reply_message} placeholder="Type your reply here..." rows="4" required></textarea>
    </div>

    <div class="modal-actions">
      <button type="button" class="btn btn-outline" onclick={() => showModal = false}>Cancel</button>
      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={14} class="animate-spin" />
          <span>Sending...</span>
        {:else}
          <span>Send Reply</span>
        {/if}
      </button>
    </div>
  </form>
</Modal>

<style>
  .reply-text {
    color: var(--success);
    font-weight: 500;
  }
  .feedback-context {
    background: #f8fafc;
    border-radius: var(--radius-sm);
    padding: 12px;
    margin-bottom: 16px;
    border: 1px solid var(--border);
    font-size: 13px;
  }
  .feedback-context p {
    margin-bottom: 4px;
  }
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
  }
</style>
