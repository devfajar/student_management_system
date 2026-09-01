<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Award, Save, AlertCircle, CheckCircle, Search, Loader2 } from 'lucide-svelte';

  let subjects = $state([]);
  let sessions = $state([]);
  let selectedSubject = $state('');
  let selectedSession = $state('');

  let studentsList = $state([]);
  let loadingInit = $state(true);
  let fetchingStudents = $state(false);
  let saving = $state(false);
  let error = $state('');
  let success = $state('');

  onMount(async () => {
    try {
      const [subs, sess] = await Promise.all([
        api.getSubjects(),
        api.getSessions()
      ]);
      subjects = subs;
      sessions = sess;
      if (subjects.length > 0) selectedSubject = subjects[0].id;
      if (sessions.length > 0) selectedSession = sessions[0].id;
    } catch (err) {
      error = err.message || 'Failed to load initial data';
    } finally {
      loadingInit = false;
    }
  });

  async function handleFetchStudents() {
    if (!selectedSubject || !selectedSession) {
      error = 'Please select a Subject and a Session Year';
      return;
    }
    fetchingStudents = true;
    error = '';
    success = '';
    try {
      const data = await api.getStudentsForResults(selectedSubject, selectedSession);
      studentsList = data.map(s => ({
        student_id: s.student_id,
        name: s.name,
        username: s.username,
        assignment_marks: Number(s.assignment_marks) || 0,
        exam_marks: Number(s.exam_marks) || 0
      }));
      if (studentsList.length === 0) {
        error = 'No students found in this course/session.';
      }
    } catch (err) {
      error = err.message || 'Failed to fetch students';
    } finally {
      fetchingStudents = false;
    }
  }

  function computeGrade(assignment, exam) {
    const total = (Number(assignment) || 0) + (Number(exam) || 0);
    if (total >= 90) return { grade: 'A+', class: 'badge-success' };
    if (total >= 80) return { grade: 'A', class: 'badge-success' };
    if (total >= 70) return { grade: 'B', class: 'badge-info' };
    if (total >= 60) return { grade: 'C', class: 'badge-warning' };
    if (total >= 50) return { grade: 'D', class: 'badge-warning' };
    return { grade: 'F', class: 'badge-danger' };
  }

  async function handleSaveResults() {
    saving = true;
    error = '';
    success = '';
    try {
      const payload = {
        subject_id: selectedSubject,
        student_results: studentsList.map(s => ({
          student_id: s.student_id,
          assignment_marks: Number(s.assignment_marks) || 0,
          exam_marks: Number(s.exam_marks) || 0
        }))
      };
      const res = await api.saveStudentResults(payload);
      success = res.message || 'Student marks and grades saved successfully!';
    } catch (err) {
      error = err.message || 'Failed to save student results';
    } finally {
      saving = false;
    }
  }
</script>

<div class="content-body">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <Award size={20} color="#3b82f6" />
        Add / Edit Student Examination Results
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

    {#if loadingInit}
      <div class="loading-state">
        <Loader2 size={24} class="animate-spin" color="#3b82f6" />
        <p>Loading course subjects...</p>
      </div>
    {:else}
      <div class="filters-grid">
        <div class="form-group">
          <label class="form-label" for="stf-res-subj">Select Subject</label>
          <select id="stf-res-subj" class="form-control" bind:value={selectedSubject}>
            {#each subjects as s}
              <option value={s.id}>{s.subject_name} ({s.course_name})</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label class="form-label" for="stf-res-sess">Select Session Year</label>
          <select id="stf-res-sess" class="form-control" bind:value={selectedSession}>
            {#each sessions as ses}
              <option value={ses.id}>{ses.session_start_year} to {ses.session_end_year}</option>
            {/each}
          </select>
        </div>

        <div class="form-group fetch-btn-group">
          <button class="btn btn-primary" onclick={handleFetchStudents} disabled={fetchingStudents}>
            {#if fetchingStudents}
              <Loader2 size={16} class="animate-spin" />
              <span>Fetching...</span>
            {:else}
              <Search size={16} />
              <span>Fetch Students</span>
            {/if}
          </button>
        </div>
      </div>
    {/if}
  </div>

  {#if studentsList.length > 0}
    <div class="card">
      <div class="card-header" style="justify-content: space-between;">
        <h3 class="card-title">Student Grades & Marks Entry ({studentsList.length} Students)</h3>
        <button class="btn btn-success" onclick={handleSaveResults} disabled={saving}>
          {#if saving}
            <Loader2 size={16} class="animate-spin" />
            <span>Saving Results...</span>
          {:else}
            <Save size={16} />
            <span>Save All Results</span>
          {/if}
        </button>
      </div>

      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Student Name</th>
              <th>Username</th>
              <th style="width: 150px;">Assignment Marks (Max: 50)</th>
              <th style="width: 150px;">Exam Marks (Max: 50)</th>
              <th>Total Marks</th>
              <th>Predicted Grade</th>
            </tr>
          </thead>
          <tbody>
            {#each studentsList as student, index}
              {@const total = (Number(student.assignment_marks) || 0) + (Number(student.exam_marks) || 0)}
              {@const gradeInfo = computeGrade(student.assignment_marks, student.exam_marks)}
              <tr>
                <td>{index + 1}</td>
                <td><strong>{student.name}</strong></td>
                <td><code>{student.username}</code></td>
                <td>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    step="0.5"
                    class="form-control mark-input"
                    bind:value={student.assignment_marks}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    step="0.5"
                    class="form-control mark-input"
                    bind:value={student.exam_marks}
                  />
                </td>
                <td><strong>{total.toFixed(1)} / 100</strong></td>
                <td>
                  <span class="badge {gradeInfo.class}">{gradeInfo.grade}</span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <div class="card-footer-actions">
        <button class="btn btn-success" onclick={handleSaveResults} disabled={saving}>
          {#if saving}
            <Loader2 size={16} class="animate-spin" />
            <span>Saving Results...</span>
          {:else}
            <Save size={16} />
            <span>Save All Results</span>
          {/if}
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    align-items: flex-end;
  }
  .fetch-btn-group {
    display: flex;
    align-items: flex-end;
  }
  .mark-input {
    width: 120px;
    font-weight: 600;
  }
  .card-footer-actions {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  .loading-state {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
  }
</style>
