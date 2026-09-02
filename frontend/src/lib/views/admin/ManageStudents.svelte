<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import { UserPlus, Edit2, Trash2, Search, AlertCircle, CheckCircle, Loader2, Camera, User, FileDown } from 'lucide-svelte';

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
  let profilePicFile = $state(null);
  let profilePicPreview = $state('');

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

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      profilePicFile = file;
      profilePicPreview = URL.createObjectURL(file);
    }
  }

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
    profilePicFile = null;
    profilePicPreview = '';
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
    profilePicFile = null;
    profilePicPreview = student.profile_pic || '';
    showModal = true;
  }

  async function handleSave(e) {
    e.preventDefault();
    error = '';
    success = '';
    submitting = true;

    try {
      const formData = new FormData();
      formData.append('first_name', first_name);
      formData.append('last_name', last_name);
      formData.append('username', username);
      formData.append('email', email);
      formData.append('gender', gender);
      formData.append('course_id', course_id);
      formData.append('session_year_id', session_year_id);
      formData.append('address', address);
      if (password) formData.append('password', password);
      if (profilePicFile) formData.append('profile_pic', profilePicFile);

      if (isEditing) {
        await api.updateStudent(editId, formData);
        success = 'Student updated successfully!';
      } else {
        if (!password) throw new Error('Password is required when adding a new student');
        await api.createStudent(formData);
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

<div class="space-y-6 animate-in fade-in duration-200">
  <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <User class="text-blue-600" size={28} />
        Manage Students
      </h1>
      <p class="text-sm text-slate-500 mt-1">Enroll new students, update profiles, manage avatars and course assignments</p>
    </div>
    <div class="flex items-center gap-2.5 self-start sm:self-auto">
      <button
        class="flex items-center gap-2 px-3.5 py-2.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-sm font-semibold shadow-sm transition-all"
        onclick={() => api.exportStudentsCsv()}
      >
        <FileDown size={16} class="text-blue-600" />
        <span>Export Roster (CSV)</span>
      </button>
      <button class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all" onclick={openAddModal}>
        <UserPlus size={16} />
        <span>Add Student</span>
      </button>
    </div>
  </div>

  {#if success}
    <div class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl flex items-center gap-2 text-sm shadow-sm">
      <CheckCircle size={18} />
      <span>{success}</span>
    </div>
  {/if}

  {#if error}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-2 text-sm shadow-sm">
      <AlertCircle size={18} />
      <span>{error}</span>
    </div>
  {/if}

  <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center">
    <div class="relative w-full max-w-md">
      <Search size={16} class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
      <input
        type="text"
        class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        placeholder="Search students by name, email, course..."
        bind:value={searchQuery}
      />
    </div>
  </div>

  <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
    {#if loading}
      <div class="p-12 text-center text-slate-400">
        <Loader2 size={32} class="animate-spin mx-auto mb-2 text-blue-500" />
        <p class="text-sm">Loading student records...</p>
      </div>
    {:else if filteredStudents.length === 0}
      <div class="p-12 text-center text-slate-400">
        <p class="text-sm font-medium">No student records found.</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-200/80 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-4">Student</th>
              <th class="py-3 px-4">Username</th>
              <th class="py-3 px-4">Email</th>
              <th class="py-3 px-4">Gender</th>
              <th class="py-3 px-4">Course</th>
              <th class="py-3 px-4">Session</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            {#each filteredStudents as student}
              <tr class="hover:bg-slate-50/60 transition-colors">
                <td class="py-3 px-4 font-semibold text-slate-800">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs overflow-hidden shadow-inner flex-shrink-0">
                      {#if student.profile_pic}
                        <img src={student.profile_pic} alt="Avatar" class="w-full h-full object-cover" />
                      {:else}
                        <span>{(student.admin?.first_name?.[0] || student.admin?.username?.[0] || 'S').toUpperCase()}</span>
                      {/if}
                    </div>
                    <div>
                      <div>{student.admin?.first_name || ''} {student.admin?.last_name || ''}</div>
                      <div class="text-[11px] text-slate-400">ID #{student.id}</div>
                    </div>
                  </div>
                </td>
                <td class="py-3 px-4 font-mono text-xs text-slate-600">@{student.admin?.username}</td>
                <td class="py-3 px-4 text-slate-600 text-xs">{student.admin?.email}</td>
                <td class="py-3 px-4 text-slate-600 text-xs">{student.gender}</td>
                <td class="py-3 px-4">
                  <span class="px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 font-medium text-xs">
                    {student.course_name || '-'}
                  </span>
                </td>
                <td class="py-3 px-4 text-xs text-slate-500">{student.session_year || '-'}</td>
                <td class="py-3 px-4 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <button class="p-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-all" onclick={() => openEditModal(student)} title="Edit Student">
                      <Edit2 size={15} />
                    </button>
                    <button class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all" onclick={() => handleDelete(student.id)} title="Delete Student">
                      <Trash2 size={15} />
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

<Modal show={showModal} title={isEditing ? 'Edit Student Profile' : 'Enroll New Student'} onclose={() => showModal = false}>
  <form onsubmit={handleSave} class="space-y-4">
    <!-- Avatar Upload in Modal -->
    <div class="flex items-center gap-4 pb-3 border-b border-slate-100">
      <div class="relative">
        <div class="w-16 h-16 rounded-full overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400 font-bold text-lg shadow-inner">
          {#if profilePicPreview}
            <img src={profilePicPreview} alt="Preview" class="w-full h-full object-cover" />
          {:else}
            <span>{first_name?.[0]?.toUpperCase() || 'S'}</span>
          {/if}
        </div>
        <label class="absolute bottom-0 right-0 w-6 h-6 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center cursor-pointer shadow-sm">
          <Camera size={12} />
          <input type="file" accept="image/*" class="hidden" onchange={handleFileChange} />
        </label>
      </div>
      <div class="text-xs text-slate-500">
        <div class="font-semibold text-slate-700">Student Profile Photo</div>
        <div>Upload PNG or JPG avatar image</div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-fn">First Name</label>
        <input id="stud-fn" type="text" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={first_name} required />
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-ln">Last Name</label>
        <input id="stud-ln" type="text" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={last_name} required />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-un">Username</label>
        <input id="stud-un" type="text" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={username} required />
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-em">Email</label>
        <input id="stud-em" type="email" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={email} required />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-gen">Gender</label>
        <select id="stud-gen" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={gender}>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-pw">{isEditing ? 'Password (leave blank to keep)' : 'Password'}</label>
        <input id="stud-pw" type="password" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={password} required={!isEditing} />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-course">Course</label>
        <select id="stud-course" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={course_id} required>
          {#each courses as c}
            <option value={c.id}>{c.course_name}</option>
          {/each}
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-sess">Session Year</label>
        <select id="stud-sess" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={session_year_id} required>
          {#each sessions as s}
            <option value={s.id}>{s.session_start_year} TO {s.session_end_year}</option>
          {/each}
        </select>
      </div>
    </div>

    <div>
      <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" for="stud-addr">Residential Address</label>
      <textarea id="stud-addr" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" bind:value={address} rows="2"></textarea>
    </div>

    <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
      <button type="button" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-medium transition-all" onclick={() => showModal = false}>Cancel</button>
      <button type="submit" class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all" disabled={submitting}>
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

