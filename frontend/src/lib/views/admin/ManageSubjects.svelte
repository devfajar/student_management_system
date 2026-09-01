<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import { Plus, Edit2, Trash2, BookOpen, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let subjects = $state([]);
  let courses = $state([]);
  let staffList = $state([]);
  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

  // Modal
  let showModal = $state(false);
  let isEditing = $state(false);
  let editId = $state(null);
  let subject_name = $state('');
  let course_id = $state('');
  let staff_id = $state('');

  async function loadData() {
    loading = true;
    try {
      const [subs, crs, stfs] = await Promise.all([
        api.getSubjects(),
        api.getCourses(),
        api.getStaffList()
      ]);
      subjects = subs;
      courses = crs;
      staffList = stfs;
    } catch (err) {
      error = err.message || 'Failed to load subject data';
    } finally {
      loading = false;
    }
  }

  onMount(loadData);

  function openAddModal() {
    isEditing = false;
    editId = null;
    subject_name = '';
    course_id = courses[0]?.id || '';
    staff_id = staffList[0]?.admin?.id || '';
    showModal = true;
  }

  function openEditModal(s) {
    isEditing = true;
    editId = s.id;
    subject_name = s.subject_name;
    course_id = s.course_id?.id || s.course_id || '';
    staff_id = s.staff_id?.id || s.staff_id || '';
    showModal = true;
  }

  async function handleSave(e) {
    e.preventDefault();
    error = '';
    success = '';
    submitting = true;

    try {
      const payload = {
        subject_name,
        course_id: Number(course_id),
        staff_id: Number(staff_id)
      };

      if (isEditing) {
        await api.updateSubject(editId, payload);
        success = 'Subject updated successfully!';
      } else {
        await api.createSubject(payload);
        success = 'Subject created successfully!';
      }
      showModal = false;
      await loadData();
    } catch (err) {
      error = err.message || 'Failed to save subject';
    } finally {
      submitting = false;
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this subject?')) return;
    try {
      await api.deleteSubject(id);
      success = 'Subject deleted successfully!';
      await loadData();
    } catch (err) {
      error = err.message || 'Failed to delete subject';
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <BookOpen size={20} color="#3b82f6" />
        Manage Subjects
      </h2>
      <button class="btn btn-primary" onclick={openAddModal}>
        <Plus size={16} />
        <span>Add Subject</span>
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
        <p>Loading subjects...</p>
      </div>
    {:else if subjects.length === 0}
      <div class="empty-state">
        <p>No subjects found. Click "Add Subject" to create one.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Subject Name</th>
              <th>Course</th>
              <th>Assigned Staff</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each subjects as s}
              <tr>
                <td>#{s.id}</td>
                <td><strong>{s.subject_name}</strong></td>
                <td><span class="badge badge-info">{s.course_name || '-'}</span></td>
                <td>{s.staff_name || '-'}</td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick={() => openEditModal(s)}>
                      <Edit2 size={14} />
                      <span>Edit</span>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick={() => handleDelete(s.id)}>
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

<Modal show={showModal} title={isEditing ? 'Edit Subject' : 'Add New Subject'} onclose={() => showModal = false}>
  <form onsubmit={handleSave}>
    <div class="form-group">
      <label class="form-label" for="subj-name">Subject Name</label>
      <input
        id="subj-name"
        type="text"
        class="form-control"
        placeholder="e.g. Data Structures, Thermodynamics"
        bind:value={subject_name}
        required
      />
    </div>

    <div class="form-group">
      <label class="form-label" for="subj-course">Course</label>
      <select id="subj-course" class="form-control" bind:value={course_id} required>
        {#each courses as c}
          <option value={c.id}>{c.course_name}</option>
        {/each}
      </select>
    </div>

    <div class="form-group">
      <label class="form-label" for="subj-staff">Assigned Staff</label>
      <select id="subj-staff" class="form-control" bind:value={staff_id} required>
        {#each staffList as st}
          <option value={st.admin?.id}>{st.admin?.first_name} {st.admin?.last_name} ({st.admin?.username})</option>
        {/each}
      </select>
    </div>

    <div class="modal-actions">
      <button type="button" class="btn btn-outline" onclick={() => showModal = false}>Cancel</button>
      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={14} class="animate-spin" />
          <span>Saving...</span>
        {:else}
          <span>{isEditing ? 'Save Changes' : 'Create Subject'}</span>
        {/if}
      </button>
    </div>
  </form>
</Modal>

<style>
  .action-buttons {
    display: flex;
    gap: 8px;
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
