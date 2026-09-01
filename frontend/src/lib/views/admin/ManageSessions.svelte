<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import { Plus, Trash2, Calendar, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let sessions = $state([]);
  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

  // Modal
  let showModal = $state(false);
  let session_start_year = $state('');
  let session_end_year = $state('');

  async function loadSessions() {
    loading = true;
    try {
      sessions = await api.getSessions();
    } catch (err) {
      error = err.message || 'Failed to load sessions';
    } finally {
      loading = false;
    }
  }

  onMount(loadSessions);

  function openAddModal() {
    session_start_year = '';
    session_end_year = '';
    showModal = true;
  }

  async function handleSave(e) {
    e.preventDefault();
    error = '';
    success = '';
    submitting = true;
    try {
      await api.createSession({ session_start_year, session_end_year });
      success = 'Session year added successfully!';
      showModal = false;
      await loadSessions();
    } catch (err) {
      error = err.message || 'Failed to save session year';
    } finally {
      submitting = false;
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this session year?')) return;
    try {
      await api.deleteSession(id);
      success = 'Session year deleted successfully!';
      await loadSessions();
    } catch (err) {
      error = err.message || 'Failed to delete session';
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <Calendar size={20} color="#3b82f6" />
        Session Years
      </h2>
      <button class="btn btn-primary" onclick={openAddModal}>
        <Plus size={16} />
        <span>Add Session Year</span>
      </button>
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
        <p>Loading sessions...</p>
      </div>
    {:else if sessions.length === 0}
      <div class="empty-state">
        <p>No session years found. Click "Add Session Year" to create one.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Session Start Date</th>
              <th>Session End Date</th>
              <th>Display</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each sessions as s}
              <tr>
                <td>#{s.id}</td>
                <td>{s.session_start_year}</td>
                <td>{s.session_end_year}</td>
                <td><span class="badge badge-info">{s.session_start_year} TO {s.session_end_year}</span></td>
                <td>
                  <button class="btn btn-danger btn-sm" onclick={() => handleDelete(s.id)}>
                    <Trash2 size={14} />
                    <span>Delete</span>
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

<Modal show={showModal} title="Add New Session Year" onclose={() => showModal = false}>
  <form onsubmit={handleSave}>
    <div class="form-group">
      <label class="form-label" for="sess-start">Session Start Date</label>
      <input id="sess-start" type="date" class="form-control" bind:value={session_start_year} required />
    </div>

    <div class="form-group">
      <label class="form-label" for="sess-end">Session End Date</label>
      <input id="sess-end" type="date" class="form-control" bind:value={session_end_year} required />
    </div>

    <div class="modal-actions">
      <button type="button" class="btn btn-outline" onclick={() => showModal = false}>Cancel</button>
      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={14} class="animate-spin" />
          <span>Saving...</span>
        {:else}
          <span>Create Session</span>
        {/if}
      </button>
    </div>
  </form>
</Modal>

<style>
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
