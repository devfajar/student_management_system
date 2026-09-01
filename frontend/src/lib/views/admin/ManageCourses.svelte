<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import { Plus, Edit2, Trash2, GraduationCap, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let courses = $state([]);
  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state('');

  // Modal
  let showModal = $state(false);
  let isEditing = $state(false);
  let editId = $state(null);
  let course_name = $state('');

  async function loadCourses() {
    loading = true;
    try {
      courses = await api.getCourses();
    } catch (err) {
      error = err.message || 'Failed to load courses';
    } finally {
      loading = false;
    }
  }

  onMount(loadCourses);

  function openAddModal() {
    isEditing = false;
    editId = null;
    course_name = '';
    showModal = true;
  }

  function openEditModal(c) {
    isEditing = true;
    editId = c.id;
    course_name = c.course_name;
    showModal = true;
  }

  async function handleSave(e) {
    e.preventDefault();
    error = '';
    success = '';
    submitting = true;
    try {
      if (isEditing) {
        await api.updateCourse(editId, course_name);
        success = 'Course updated successfully!';
      } else {
        await api.createCourse(course_name);
        success = 'Course created successfully!';
      }
      showModal = false;
      await loadCourses();
    } catch (err) {
      error = err.message || 'Failed to save course';
    } finally {
      submitting = false;
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this course? All associated subjects may also be affected.')) return;
    try {
      await api.deleteCourse(id);
      success = 'Course deleted successfully!';
      await loadCourses();
    } catch (err) {
      error = err.message || 'Failed to delete course';
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <GraduationCap size={20} color="#3b82f6" />
        Manage Courses
      </h2>
      <button class="btn btn-primary" onclick={openAddModal}>
        <Plus size={16} />
        <span>Add Course</span>
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
        <p>Loading courses...</p>
      </div>
    {:else if courses.length === 0}
      <div class="empty-state">
        <p>No courses found. Click "Add Course" to create one.</p>
      </div>
    {:else}
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Course Name</th>
              <th>Created Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each courses as c}
              <tr>
                <td>#{c.id}</td>
                <td><strong>{c.course_name}</strong></td>
                <td>{new Date(c.created_at).toLocaleDateString()}</td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick={() => openEditModal(c)}>
                      <Edit2 size={14} />
                      <span>Edit</span>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick={() => handleDelete(c.id)}>
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

<Modal show={showModal} title={isEditing ? 'Edit Course' : 'Add New Course'} onclose={() => showModal = false}>
  <form onsubmit={handleSave}>
    <div class="form-group">
      <label class="form-label" for="course-name">Course Name</label>
      <input
        id="course-name"
        type="text"
        class="form-control"
        placeholder="e.g. Computer Science, Mechanical Engineering"
        bind:value={course_name}
        required
      />
    </div>

    <div class="modal-actions">
      <button type="button" class="btn btn-outline" onclick={() => showModal = false}>Cancel</button>
      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={14} class="animate-spin" />
          <span>Saving...</span>
        {:else}
          <span>{isEditing ? 'Save Changes' : 'Create Course'}</span>
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
