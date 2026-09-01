<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Send, MessageSquare, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let feedbackHistory = $state([]);
  let feedbackText = $state('');

  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

  async function loadFeedback() {
    loading = true;
    try {
      feedbackHistory = await api.getStudentFeedback();
    } catch (err) {
      error = err.message || 'Failed to load feedback history';
    } finally {
      loading = false;
    }
  }

  onMount(loadFeedback);

  async function handleSubmit(e) {
    e.preventDefault();
    submitting = true;
    error = '';
    success = '';

    try {
      await api.sendStudentFeedback(feedbackText);
      success = 'Feedback submitted successfully!';
      feedbackText = '';
      await loadFeedback();
    } catch (err) {
      error = err.message || 'Failed to send feedback';
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
        Send Feedback to Admin
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

    <form onsubmit={handleSubmit}>
      <div class="form-group">
        <label class="form-label" for="stud-fb-text">Your Feedback / Suggestion</label>
        <textarea
          id="stud-fb-text"
          class="form-control"
          bind:value={feedbackText}
          placeholder="Type your feedback, questions, or message..."
          rows="4"
          required
        ></textarea>
      </div>

      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={16} class="animate-spin" />
          <span>Sending...</span>
        {:else}
          <Send size={16} />
          <span>Submit Feedback</span>
        {/if}
      </button>
    </form>
  </div>

  <div class="card">
    <div class="card-header">
      <h3 class="card-title">Feedback & Reply History</h3>
    </div>

    {#if loading}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading history...</p>
      </div>
    {:else if feedbackHistory.length === 0}
      <div class="empty-state">
        <p>No feedback sent yet.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Your Message</th>
              <th>Sent Date</th>
              <th>Admin Reply</th>
            </tr>
          </thead>
          <tbody>
            {#each feedbackHistory as item}
              <tr>
                <td>#{item.id}</td>
                <td>{item.feedback}</td>
                <td>{new Date(item.created_at).toLocaleDateString()}</td>
                <td>
                  {#if item.feedback_reply}
                    <span class="reply-text">{item.feedback_reply}</span>
                  {:else}
                    <span class="badge badge-warning">Awaiting Reply</span>
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
  .reply-text {
    color: var(--success);
    font-weight: 500;
  }
  .loading-state, .empty-state {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
  }
</style>
