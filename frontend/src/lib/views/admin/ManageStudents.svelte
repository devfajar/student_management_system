<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import { UserPlus, Edit2, Trash2, Search, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';

  let studentList = $state([]);
  let courses = $state([]);
  let sessions = $state([]);
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
  let gender = $state('Male');
  let course_id = $state('');
  let session_year_id = $state('');
  let address = $state('');

  const filteredStudents = $derived(
    studentList.filter(s => {
      const q = searchQuery.toLowerCase();
      const name = `${s.admin?.first_name || ''} ${s.admin?.last_name || ''}`.toLowerCase();
      const u = (s.admin?.username || '').toLowerCase();
      const e = (s.admin?.email || '').toLowerCase();
      const c = (s.course_name || '').toLowerCase();
      return name.includes(q) || u.includes(q) || e.includes(q) || c.includes(q);
    })
  );

  async function loadData() {
    loading = true;
    try {
      const [studs, crs, sess] = await Promise.all([
        api.getStudentsList(),
        api.getCourses(),
        api.getSessions()
      ]);
      studentList = studs;
      courses = crs;
      sessions = sess;
    } catch (err) {
      error = err.message || 'Failed to load student data';
    } finally {
      loading = false;
    }
  }

  onMount(loadData);

  function openAddModal() {
    isEditing = false;
    editId = null;
    first_name = '';
    last_name = '';
    username = '';
    email = '';
    password = '';
    gender = 'Male';
    course_id = courses[0]?.id || '';
    session_year_id = sessions[0]?.id || '';
    address = '';
    showModal = true;
  }

  function openEditModal(student) {
    isEditing = true;
    editId = student.id;
    first_name = student.admin?.first_name || '';
    last_name = student.admin?.last_name || '';
    username = student.admin?.username || '';
    email = student.admin?.email || '';
    password = '';
    gender = student.gender || 'Male';
    course_id = student.course_id?.id || student.course_id || '';
    session_year_id = student.session_year_id?.id || student.session_year_id || '';
    address = student.address || '';
    showModal = true;
  }

  async function handleSave(e) {
    e.preventDefault();
    error = '';
    success = '';
    submitting = true;

    try {
      const payload = {
        first_name,
        last_name,
        username,
        email,
        gender,
        course_id: Number(course_id),
        session_year_id: Number(session_year_id),
        address
      };
      if (password) payload.password = password;

      if (isEditing) {
        await api.updateStudent(editId, payload);
        success = 'Student updated successfully!';
      } else {
        if (!password) throw new Error('Password is required when adding a new student');
        await api.createStudent(payload);
        success = 'Student created successfully!';
      }
      showModal = false;
      await loadData();
    } catch (err) {
      error = err.message || 'Failed to save student';
    } finally {
      submitting = false;
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this student?')) return;
    try {
      await api.deleteStudent(id);
      success = 'Student deleted successfully!';
      await loadData();
    } catch (err) {
      error = err.message || 'Failed to delete student';
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">Manage Students</h2>
      <button class="btn btn-primary" onclick={openAddModal}>
        <UserPlus size={16} />
        <span>Add Student</span>
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
          placeholder="Search students by name, email, course..."
          bind:value={searchQuery}
        />
      </div>
    </div>

    {#if loading}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading students...</p>
      </div>
    {:else if filteredStudents.length === 0}
      <div class="empty-state">
        <p>No student records found.</p>
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
              <th>Gender</th>
              <th>Course</th>
              <th>Session</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredStudents as student}
              <tr>
                <td>#{student.id}</td>
                <td><strong>{student.admin?.first_name || ''} {student.admin?.last_name || ''}</strong></td>
                <td><code>{student.admin?.username}</code></td>
                <td>{student.admin?.email}</td>
                <td>{student.gender}</td>
                <td><span class="badge badge-info">{student.course_name || '-'}</span></td>
                <td><small>{student.session_year || '-'}</small></td>
                <td>
                  <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick={() => openEditModal(student)}>
                      <Edit2 size={14} />
                      <span>Edit</span>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick={() => handleDelete(student.id)}>
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

<Modal show={showModal} title={isEditing ? 'Edit Student' : 'Add New Student'} onclose={() => showModal = false}>
  <form onsubmit={handleSave}>
    <div class="row-2">
      <div class="form-group">
        <label class="form-label" for="stud-fn">First Name</label>
        <input id="stud-fn" type="text" class="form-control" bind:value={first_name} required />
      </div>
      <div class="form-group">
        <label class="form-label" for="stud-ln">Last Name</label>
        <input id="stud-ln" type="text" class="form-control" bind:value={last_name} required />
      </div>
    </div>

    <div class="row-2">
      <div class="form-group">
        <label class="form-label" for="stud-un">Username</label>
        <input id="stud-un" type="text" class="form-control" bind:value={username} required />
      </div>
      <div class="form-group">
        <label class="form-label" for="stud-em">Email</label>
        <input id="stud-em" type="email" class="form-control" bind:value={email} required />
      </div>
    </div>

    <div class="row-2">
      <div class="form-group">
        <label class="form-label" for="stud-gen">Gender</label>
        <select id="stud-gen" class="form-control" bind:value={gender}>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label" for="stud-pw">{isEditing ? 'Password (leave blank to keep unchanged)' : 'Password'}</label>
        <input id="stud-pw" type="password" class="form-control" bind:value={password} required={!isEditing} />
      </div>
    </div>

    <div class="row-2">
      <div class="form-group">
        <label class="form-label" for="stud-course">Course</label>
        <select id="stud-course" class="form-control" bind:value={course_id} required>
          {#each courses as c}
            <option value={c.id}>{c.course_name}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="stud-sess">Session Year</label>
        <select id="stud-sess" class="form-control" bind:value={session_year_id} required>
          {#each sessions as s}
            <option value={s.id}>{s.session_start_year} TO {s.session_end_year}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="stud-addr">Address</label>
      <textarea id="stud-addr" class="form-control" bind:value={address} rows="2"></textarea>
    </div>

    <div class="modal-actions">
      <button type="button" class="btn btn-outline" onclick={() => showModal = false}>Cancel</button>
      <button type="submit" class="btn btn-primary" disabled={submitting}>
        {#if submitting}
          <Loader2 size={14} class="animate-spin" />
          <span>Saving...</span>
        {:else}
          <span>{isEditing ? 'Save Changes' : 'Create Student'}</span>
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
