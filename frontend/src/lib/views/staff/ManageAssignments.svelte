<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { auth } from '../../authStore.svelte.js';
  import {
    BookOpen,
    Plus,
    Calendar,
    Award,
    Users,
    Paperclip,
    Trash2,
    CheckCircle2,
    Clock,
    AlertCircle,
    Eye,
    X,
    FileText,
    Download
  } from 'lucide-svelte';

  let assignments = $state([]);
  let subjects = $state([]);
  let sessions = $state([]);
  let loading = $state(true);
  let error = $state('');
  let success = $state('');
  let selectedSubject = $state('');

  // Create Assignment Modal
  let showCreateModal = $state(false);
  let submitting = $state(false);
  let formSubjectId = $state('');
  let formSessionId = $state('');
  let formTitle = $state('');
  let formDescription = $state('');
  let formDeadline = $state('');
  let formMaxMarks = $state(100);
  let formAttachment = $state(null);

  // View Submissions Modal
  let showSubmissionsModal = $state(false);
  let selectedAssignment = $state(null);
  let submissions = $state([]);
  let loadingSubmissions = $state(false);

  // Grade Modal State
  let gradingSubmission = $state(null);
  let gradeMarks = $state('');
  let gradeFeedback = $state('');
  let savingGrade = $state(false);

  onMount(async () => {
    await loadInitialData();
  });

  async function loadInitialData() {
    loading = true;
    error = '';
    try {
      const [assignRes, subRes, sessRes] = await Promise.all([
        api.getAssignments(),
        api.getSubjects(),
        api.getSessions()
      ]);
      assignments = assignRes;
      subjects = subRes;
      sessions = sessRes;
      if (subjects.length > 0) formSubjectId = subjects[0].id;
      if (sessions.length > 0) formSessionId = sessions[0].id;
    } catch (err) {
      error = err.message || 'Failed to load assignments';
    } finally {
      loading = false;
    }
  }

  async function handleFilter() {
    loading = true;
    try {
      const params = {};
      if (selectedSubject) params.subject_id = selectedSubject;
      assignments = await api.getAssignments(params);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
      formAttachment = file;
    }
  }

  async function handleCreateAssignment() {
    if (!formSubjectId || !formSessionId || !formTitle || !formDeadline) {
      error = 'Please fill out all required fields';
      return;
    }

    submitting = true;
    error = '';
    success = '';

    try {
      const fd = new FormData();
      fd.append('subject_id', formSubjectId);
      fd.append('session_year_id', formSessionId);
      fd.append('title', formTitle);
      fd.append('description', formDescription);
      fd.append('deadline', new Date(formDeadline).toISOString());
      fd.append('max_marks', formMaxMarks);
      if (formAttachment) {
        fd.append('attachment', formAttachment);
      }

      await api.createAssignment(fd);
      success = 'Assignment published successfully!';
      showCreateModal = false;
      // Reset form
      formTitle = '';
      formDescription = '';
      formDeadline = '';
      formAttachment = null;
      await handleFilter();
    } catch (err) {
      error = err.message || 'Failed to create assignment';
    } finally {
      submitting = false;
    }
  }

  async function handleDeleteAssignment(id, title) {
    if (!confirm(`Are you sure you want to delete assignment "${title}"?`)) return;
    try {
      await api.deleteAssignment(id);
      success = `Deleted assignment "${title}"`;
      await handleFilter();
    } catch (err) {
      error = err.message || 'Failed to delete assignment';
    }
  }

  async function openSubmissions(assign) {
    selectedAssignment = assign;
    showSubmissionsModal = true;
    loadingSubmissions = true;
    gradingSubmission = null;
    try {
      submissions = await api.getAssignmentSubmissions(assign.id);
    } catch (err) {
      error = err.message || 'Failed to fetch student submissions';
    } finally {
      loadingSubmissions = false;
    }
  }

  function startGrading(sub) {
    gradingSubmission = sub;
    gradeMarks = sub.marks_obtained !== null ? sub.marks_obtained : '';
    gradeFeedback = sub.feedback_remarks || '';
  }

  async function handleSaveGrade() {
    if (!gradingSubmission) return;
    if (gradeMarks === '' || isNaN(gradeMarks)) {
      alert('Please enter valid numeric marks');
      return;
    }

    savingGrade = true;
    try {
      const updated = await api.gradeAssignmentSubmission(gradingSubmission.id, {
        marks_obtained: parseFloat(gradeMarks),
        feedback_remarks: gradeFeedback
      });

      // Update in local list
      submissions = submissions.map(s => s.id === updated.id ? updated : s);
      gradingSubmission = null;
      success = `Grade saved for ${updated.student_name}!`;
    } catch (err) {
      alert(err.message || 'Failed to save grade');
    } finally {
      savingGrade = false;
    }
  }

  function formatDateTime(str) {
    if (!str) return 'N/A';
    return new Date(str).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  }

  function isOverdue(deadline) {
    return new Date(deadline) < new Date();
  }
</script>

<div class="space-y-6">
  <!-- Page Header & Action Toolbar -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
        <BookOpen class="w-6 h-6" />
      </div>
      <div>
        <h1 class="text-xl font-bold text-slate-800">Course Syllabus & Assignments</h1>
        <p class="text-sm text-slate-500">Publish coursework, evaluate student submissions, and record marks</p>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <select
        bind:value={selectedSubject}
        onchange={handleFilter}
        class="px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
      >
        <option value="">All Subjects</option>
        {#each subjects as sub}
          <option value={sub.id}>{sub.subject_name}</option>
        {/each}
      </select>

      <button
        onclick={() => showCreateModal = true}
        class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all shadow-blue-500/10 hover:shadow-blue-500/20"
      >
        <Plus class="w-4 h-4" />
        New Assignment
      </button>
    </div>
  </div>

  <!-- Status Alerts -->
  {#if error}
    <div class="flex items-center gap-2 p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-sm">
      <AlertCircle class="w-5 h-5 flex-shrink-0" />
      <span>{error}</span>
      <button onclick={() => error = ''} class="ml-auto text-rose-500 hover:text-rose-700">&times;</button>
    </div>
  {/if}

  {#if success}
    <div class="flex items-center gap-2 p-4 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-sm">
      <CheckCircle2 class="w-5 h-5 flex-shrink-0" />
      <span>{success}</span>
      <button onclick={() => success = ''} class="ml-auto text-emerald-500 hover:text-emerald-700">&times;</button>
    </div>
  {/if}

  <!-- Assignment Cards Grid -->
  {#if loading}
    <div class="flex justify-center items-center py-20">
      <div class="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  {:else if assignments.length === 0}
    <div class="bg-white rounded-2xl border border-slate-100 p-12 text-center shadow-sm">
      <div class="w-16 h-16 bg-slate-100 text-slate-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <BookOpen class="w-8 h-8" />
      </div>
      <h3 class="text-base font-bold text-slate-800 mb-1">No Assignments Found</h3>
      <p class="text-sm text-slate-500 mb-4">You haven't posted any assignments yet or no courses match the filter.</p>
      <button
        onclick={() => showCreateModal = true}
        class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition"
      >
        <Plus class="w-4 h-4" />
        Create First Assignment
      </button>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each assignments as assign (assign.id)}
        <div class="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between">
          <div>
            <!-- Header Badges -->
            <div class="flex items-center justify-between gap-2 mb-3">
              <span class="px-2.5 py-1 bg-blue-50 text-blue-700 font-semibold text-xs rounded-lg border border-blue-100">
                {assign.subject_name}
              </span>
              {#if isOverdue(assign.deadline)}
                <span class="px-2 py-0.5 bg-rose-50 text-rose-600 font-medium text-xs rounded-md border border-rose-100 flex items-center gap-1">
                  <Clock class="w-3 h-3" /> Closed
                </span>
              {:else}
                <span class="px-2 py-0.5 bg-emerald-50 text-emerald-600 font-medium text-xs rounded-md border border-emerald-100 flex items-center gap-1">
                  <Clock class="w-3 h-3" /> Active
                </span>
              {/if}
            </div>

            <!-- Title & Description -->
            <h3 class="text-base font-bold text-slate-800 mb-1.5">{assign.title}</h3>
            <p class="text-xs text-slate-500 line-clamp-3 mb-4 leading-relaxed">{assign.description || 'No detailed instructions provided.'}</p>

            <!-- Metrics -->
            <div class="space-y-2 border-t border-slate-100 pt-3 text-xs text-slate-600">
              <div class="flex items-center justify-between">
                <span class="flex items-center gap-1.5 text-slate-500">
                  <Calendar class="w-3.5 h-3.5 text-slate-400" /> Due Date:
                </span>
                <span class="font-medium text-slate-700">{formatDateTime(assign.deadline)}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="flex items-center gap-1.5 text-slate-500">
                  <Award class="w-3.5 h-3.5 text-slate-400" /> Max Score:
                </span>
                <span class="font-bold text-blue-600">{assign.max_marks} pts</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="flex items-center gap-1.5 text-slate-500">
                  <Users class="w-3.5 h-3.5 text-slate-400" /> Submissions:
                </span>
                <span class="font-bold text-slate-800">{assign.submissions_count} submitted</span>
              </div>
            </div>
          </div>

          <!-- Card Actions -->
          <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
            {#if assign.attachment}
              <a
                href={assign.attachment}
                target="_blank"
                rel="noreferrer"
                class="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition"
                title="Download Assignment Material"
              >
                <Paperclip class="w-4 h-4" />
              </a>
            {/if}

            <div class="flex items-center gap-2 ml-auto">
              <button
                onclick={() => openSubmissions(assign)}
                class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold rounded-xl text-xs transition"
              >
                <Eye class="w-3.5 h-3.5" /> Submissions ({assign.submissions_count})
              </button>
              <button
                onclick={() => handleDeleteAssignment(assign.id, assign.title)}
                class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition"
                title="Delete Assignment"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Modal: Create New Assignment -->
{#if showCreateModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
        <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2">
          <BookOpen class="w-5 h-5 text-blue-600" />
          Publish New Assignment
        </h3>
        <button onclick={() => showCreateModal = false} class="text-slate-400 hover:text-slate-600">
          <X class="w-5 h-5" />
        </button>
      </div>

      <form onsubmit={(e) => { e.preventDefault(); handleCreateAssignment(); }} class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Subject *</label>
            <select
              bind:value={formSubjectId}
              required
              class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            >
              {#each subjects as sub}
                <option value={sub.id}>{sub.subject_name}</option>
              {/each}
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Academic Session *</label>
            <select
              bind:value={formSessionId}
              required
              class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            >
              {#each sessions as sess}
                <option value={sess.id}>{sess.session_start_year} - {sess.session_end_year}</option>
              {/each}
            </select>
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Assignment Title *</label>
          <input
            type="text"
            bind:value={formTitle}
            required
            placeholder="e.g. Midterm Problem Set 2"
            class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Instructions & Description</label>
          <textarea
            bind:value={formDescription}
            rows="3"
            placeholder="Outline objectives, formatting rules, or question details..."
            class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          ></textarea>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Deadline *</label>
            <input
              type="datetime-local"
              bind:value={formDeadline}
              required
              class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Maximum Marks *</label>
            <input
              type="number"
              bind:value={formMaxMarks}
              required
              min="1"
              step="any"
              class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Attach Problem Sheet / Reference (Optional)</label>
          <input
            type="file"
            onchange={handleFileSelect}
            class="w-full text-sm text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 mt-6">
          <button
            type="button"
            onclick={() => showCreateModal = false}
            class="px-4 py-2.5 border border-slate-200 text-slate-600 font-semibold rounded-xl text-sm hover:bg-slate-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition shadow-sm disabled:opacity-50"
          >
            {submitting ? 'Publishing...' : 'Publish Assignment'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Modal: View Submissions & Grade -->
{#if showSubmissionsModal && selectedAssignment}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-3xl w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
        <div>
          <h3 class="text-lg font-bold text-slate-800">{selectedAssignment.title} — Submissions</h3>
          <p class="text-xs text-slate-500">Max Score: {selectedAssignment.max_marks} pts | Due: {formatDateTime(selectedAssignment.deadline)}</p>
        </div>
        <button onclick={() => { showSubmissionsModal = false; gradingSubmission = null; }} class="text-slate-400 hover:text-slate-600">
          <X class="w-5 h-5" />
        </button>
      </div>

      {#if loadingSubmissions}
        <div class="flex justify-center items-center py-12">
          <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      {:else if submissions.length === 0}
        <div class="text-center py-12 text-slate-500 text-sm">
          No student submissions received yet for this assignment.
        </div>
      {:else}
        <div class="space-y-4">
          {#each submissions as sub (sub.id)}
            <div class="p-4 rounded-2xl border {gradingSubmission?.id === sub.id ? 'border-blue-500 bg-blue-50/20' : 'border-slate-100 bg-slate-50/50'} transition">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                <div>
                  <h4 class="font-bold text-sm text-slate-800">{sub.student_name}</h4>
                  <p class="text-xs text-slate-500">@{sub.student_username} • Submitted {formatDateTime(sub.submitted_at)}</p>
                </div>

                <div class="flex items-center gap-2">
                  {#if sub.is_late}
                    <span class="px-2 py-0.5 bg-rose-100 text-rose-700 text-xs font-semibold rounded-md">Late</span>
                  {:else}
                    <span class="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-md">On-Time</span>
                  {/if}

                  {#if sub.status === 'Graded'}
                    <span class="px-2.5 py-0.5 bg-blue-600 text-white text-xs font-bold rounded-md">
                      {sub.marks_obtained} / {sub.max_marks} pts
                    </span>
                  {:else}
                    <span class="px-2.5 py-0.5 bg-amber-100 text-amber-800 text-xs font-semibold rounded-md">Ungraded</span>
                  {/if}
                </div>
              </div>

              <!-- Student Submission Content -->
              {#if sub.submission_text}
                <div class="p-3 bg-white border border-slate-200 rounded-xl text-xs text-slate-700 my-2 font-mono whitespace-pre-wrap">
                  {sub.submission_text}
                </div>
              {/if}

              <div class="flex items-center justify-between gap-2 pt-2 border-t border-slate-200/60 mt-2">
                <div>
                  {#if sub.submission_file}
                    <a
                      href={sub.submission_file}
                      target="_blank"
                      rel="noreferrer"
                      class="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700"
                    >
                      <Download class="w-3.5 h-3.5" /> Download Attached Deliverable
                    </a>
                  {/if}
                </div>

                <button
                  onclick={() => startGrading(sub)}
                  class="px-3 py-1 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition"
                >
                  {sub.status === 'Graded' ? 'Edit Grade' : 'Grade Submission'}
                </button>
              </div>

              <!-- Inline Grading Form -->
              {#if gradingSubmission?.id === sub.id}
                <div class="mt-4 pt-4 border-t border-blue-200 space-y-3 bg-white p-4 rounded-xl shadow-sm">
                  <h5 class="text-xs font-bold uppercase text-slate-700 tracking-wider">Evaluate & Record Marks</h5>
                  <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label class="block text-xs font-semibold text-slate-600 mb-1">Marks Obtained (Max: {selectedAssignment.max_marks})</label>
                      <input
                        type="number"
                        bind:value={gradeMarks}
                        step="any"
                        max={selectedAssignment.max_marks}
                        class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      />
                    </div>
                    <div class="sm:col-span-2">
                      <label class="block text-xs font-semibold text-slate-600 mb-1">Feedback Remarks</label>
                      <input
                        type="text"
                        bind:value={gradeFeedback}
                        placeholder="e.g. Great analysis, well structured citations."
                        class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      />
                    </div>
                  </div>
                  <div class="flex justify-end gap-2 pt-2">
                    <button
                      onclick={() => gradingSubmission = null}
                      class="px-3 py-1.5 text-xs font-semibold text-slate-500 hover:text-slate-700"
                    >
                      Cancel
                    </button>
                    <button
                      onclick={handleSaveGrade}
                      disabled={savingGrade}
                      class="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
                    >
                      {savingGrade ? 'Saving...' : 'Save Grade'}
                    </button>
                  </div>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
{/if}
