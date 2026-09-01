<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import { UserPlus, Edit2, Trash2, Search, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let staffList = $state([]);
  let searchQuery = $state('');
  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

  // Modal State
  let showModal = $state(false);
  let isEditing = $state(false);
  let editId = $state(null);

  // Form Fields
  let first_name = $state('');
  let last_name = $state('');
  let username = $state('');
  let email = $state('');
  let password = $state('');
  let address = $state('');

  const filteredStaff = $derived(
    staffList.filter(s => {
      const q = searchQuery.toLowerCase();
      const name = `${s.admin?.first_name || ''} ${s.admin?.last_name || ''}`.toLowerCase();
      const u = (s.admin?.username || '').toLowerCase();
      const e = (s.admin?.email || '').toLowerCase();
      return name.includes(q) || u.includes(q) || e.includes(q);
    })
  );

  async function loadStaff() {
    loading = true;
    try {
      staffList = await api.getStaffList();
    } catch (err) {
      error = err.message || 'Failed to load staff list';
    } finally {
      loading = false;
    }
  }

  onMount(loadStaff);

  function openAddModal() {
    isEditing = false;
    editId = null;
    first_name = '';
    last_name = '';
    username = '';
    email = '';
    password = '';
    address = '';
    showModal = true;
  }

  function openEditModal(staff) {
    isEditing = true;
    editId = staff.id;
    first_name = staff.admin?.first_name || '';
    last_name = staff.admin?.last_name || '';
    username = staff.admin?.username || '';
    email = staff.admin?.email || '';
    password = '';
    address = staff.address || '';
    showModal = true;
  }

  async function handleSave(e) {
    e.preventDefault();
    error = '';
    success = '';
    submitting = true;

    try {
      const payload = { first_name, last_name, username, email, address };
      if (password) payload.password = password;

      if (isEditing) {
        await api.updateStaff(editId, payload);
        success = 'Staff updated successfully!';
      } else {
        if (!password) throw new Error('Password is required when adding new staff');
        await api.createStaff(payload);
        success = 'Staff created successfully!';
      }
      showModal = false;
      await loadStaff();
    } catch (err) {
      error = err.message || 'Failed to save staff';
    } finally {
      submitting = false;
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this staff member?')) return;
    try {
      await api.deleteStaff(id);
      success = 'Staff deleted successfully!';
      await loadStaff();
    } catch (err) {
      error = err.message || 'Failed to delete staff';
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">Manage Staff</h2>
      <button class="btn btn-primary" onclick={openAddModal}>
        <UserPlus size={16} />
        <span>Add Staff</span>
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

    <div class="search-bar">
      <div class="search-input-wrapper">
        <Search size={16} class="search-icon" />
        <input
          type="text"
          class="form-control with-icon"
          placeholder="Search staff by name, email, or username..."
          bind:value={searchQuery}
        />
      </div>
    </div>

    {#if loading}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading staff...</p>
      </div>
    {:else if filteredStaff.length === 0}
      <div class="empty-state">
        <p>No staff records found.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Username</th>
              <th>Email</th>
              <th>Address</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredStaff as staff}
              <tr>
                <td>#{staff.id}</td>
                <td><strong>{staff.admin?.first_name || ''} {staff.admin?.last_name || ''}</strong></td>
                <td><code>{staff.admin?.username}</code></td>
                <td>{staff.admin?.email}</td>
                <td>{staff.address || '-'}</td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick={() => openEditModal(staff)}>
                      <Edit2 size={14} />
                      <span>Edit</span>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick={() => handleDelete(staff.id)}>
                      <Trash2 size={14} />
                      <span>Delete</span>
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<Modal show={showModal} title={isEditing ? 'Edit Staff' : 'Add New Staff'} onclose={() => showModal = false}>
  <form onsubmit={handleSave}>
    <div class="row-2">
      <div class="form-group">
        <label class="form-label" for="staff-fn">First Name</label>
        <input id="staff-fn" type="text" class="form-control" bind:value={first_name} required />
      </div>
      <div class="form-group">
        <label class="form-label" for="staff-ln">Last Name</label>
        <input id="staff-ln" type="text" class="form-control" bind:value={last_name} required />
      </div>
    </div>

    <div class="row-2">
      <div class="form-group">
        <label class="form-label" for="staff-un">Username</label>
        <input id="staff-un" type="text" class="form-control" bind:value={username} required />
      </div>
      <div class="form-group">
        <label class="form-label" for="staff-em">Email</label>
        <input id="staff-em" type="email" class="form-control" bind:value={email} required />
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="staff-pw">{isEditing ? 'Password (leave blank to keep unchanged)' : 'Password'}</label>
      <input id="staff-pw" type="password" class="form-control" bind:value={password} required={!isEditing} />
    </div>

    <div class="form-group">
      <label class="form-label" for="staff-addr">Address</label>
      <textarea id="staff-addr" class="form-control" bind:value={address} rows="2"></textarea>
    </div>

    <div class="modal-actions">
      <button type="button" class="btn btn-outline" onclick={() => showModal = false}>Cancel</button>
      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={14} class="animate-spin" />
          <span>Saving...</span>
        {:else}
          <span>{isEditing ? 'Save Changes' : 'Create Staff'}</span>
        {/if}
      </button>
    </div>
  </form>
</Modal>

<style>
  .search-bar {
    margin-bottom: 16px;
  }

  .search-input-wrapper {
    position: relative;
    max-width: 400px;
  }

  :global(.search-icon) {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
  }

  .with-icon {
    padding-left: 36px;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  .row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
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
