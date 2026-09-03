<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import {
    BookOpen,
    Calendar,
    Award,
    Paperclip,
    CheckCircle2,
    Clock,
    AlertCircle,
    X,
    Upload,
    Download,
    FileText,
    CheckCircle
  } from 'lucide-svelte';

  let assignments = $state([]);
  let submissions = $state([]);
  let loading = $state(true);
  let error = $state('');
  let success = $state('');
  let activeTab = $state('all'); // 'all', 'pending', 'submitted', 'graded'

  // Submit Modal
  let showSubmitModal = $state(false);
  let activeAssignment = $state(null);
  let submissionText = $state('');
  let submissionFile = $state(null);
  let submitting = $state(false);

  // View Submission Details Modal
  let showDetailModal = $state(false);
  let activeSubmission = $state(null);

  onMount(async () => {
    await loadData();
  });

  async function loadData() {
    loading = true;
    error = '';
    try {
      const [assignRes, subRes] = await Promise.all([
        api.getAssignments(),
        api.getMyAssignmentSubmissions()
      ]);
      assignments = assignRes;
      submissions = subRes;
    } catch (err) {
      error = err.message || 'Failed to load assignments';
    } finally {
      loading = false;
    }
  }

  function getSubmissionForAssignment(assignId) {
    return submissions.find(s => s.assignment_id === assignId);
  }

  function getAssignmentStatus(assign) {
    const sub = getSubmissionForAssignment(assign.id);
    if (!sub) {
      return new Date(assign.deadline) < new Date() ? 'overdue' : 'pending';
    }
    if (sub.status === 'Graded') return 'graded';
    return 'submitted';
  }

  const filteredAssignments = $derived(() => {
    if (activeTab === 'all') return assignments;
    return assignments.filter(a => {
      const status = getAssignmentStatus(a);
      if (activeTab === 'pending') return status === 'pending' || status === 'overdue';
      if (activeTab === 'submitted') return status === 'submitted';
      if (activeTab === 'graded') return status === 'graded';
      return true;
    });
  });

  const stats = $derived(() => {
    let pending = 0;
    let submitted = 0;
    let graded = 0;
    assignments.forEach(a => {
      const st = getAssignmentStatus(a);
      if (st === 'pending' || st === 'overdue') pending++;
      else if (st === 'submitted') submitted++;
      else if (st === 'graded') graded++;
    });
    return { total: assignments.length, pending, submitted, graded };
  });

  function openSubmitModal(assign) {
    activeAssignment = assign;
    const existingSub = getSubmissionForAssignment(assign.id);
    submissionText = existingSub?.submission_text || '';
    submissionFile = null;
    showSubmitModal = true;
  }

  function openDetailModal(assign) {
    activeAssignment = assign;
    activeSubmission = getSubmissionForAssignment(assign.id);
    showDetailModal = true;
  }

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      submissionFile = file;
    }
  }

  async function handleSubmitAssignment() {
    if (!submissionText && !submissionFile) {
      error = 'Please provide either text content or attach a file.';
      return;
    }

    submitting = true;
    error = '';
    success = '';

    try {
      const fd = new FormData();
      if (submissionText) fd.append('submission_text', submissionText);
      if (submissionFile) fd.append('submission_file', submissionFile);

      const res = await api.submitAssignment(activeAssignment.id, fd);

      // Update submissions list
      const idx = submissions.findIndex(s => s.assignment_id === activeAssignment.id);
      if (idx !== -1) {
        submissions[idx] = res;
      } else {
        submissions.push(res);
      }

      success = res.is_late
        ? 'Assignment submitted (marked as late submission).'
        : 'Assignment submitted on time successfully!';
      showSubmitModal = false;
    } catch (err) {
      error = err.message || 'Failed to submit assignment';
    } finally {
      submitting = false;
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
</script>

<div class="space-y-6">
  <!-- Header Banner -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
        <BookOpen class="w-6 h-6" />
      </div>
      <div>
        <h1 class="text-xl font-bold text-slate-800">My Coursework & Assignments</h1>
        <p class="text-sm text-slate-500">View upcoming deadlines, submit coursework, and track instructor feedback</p>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="flex items-center gap-2">
      <div class="px-3.5 py-2 bg-slate-50 rounded-xl border border-slate-100 text-center">
        <div class="text-xs text-slate-400 font-semibold uppercase">Pending</div>
        <div class="text-base font-bold text-amber-600">{stats().pending}</div>
      </div>
      <div class="px-3.5 py-2 bg-slate-50 rounded-xl border border-slate-100 text-center">
        <div class="text-xs text-slate-400 font-semibold uppercase">Submitted</div>
        <div class="text-base font-bold text-blue-600">{stats().submitted}</div>
      </div>
      <div class="px-3.5 py-2 bg-slate-50 rounded-xl border border-slate-100 text-center">
        <div class="text-xs text-slate-400 font-semibold uppercase">Graded</div>
        <div class="text-base font-bold text-emerald-600">{stats().graded}</div>
      </div>
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

  <!-- Tab Navigation -->
  <div class="flex items-center gap-2 border-b border-slate-200 pb-3">
    <button
      onclick={() => activeTab = 'all'}
      class="px-4 py-2 text-xs font-bold rounded-xl transition {activeTab === 'all' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'}"
    >
      All Assignments ({stats().total})
    </button>
    <button
      onclick={() => activeTab = 'pending'}
      class="px-4 py-2 text-xs font-bold rounded-xl transition {activeTab === 'pending' ? 'bg-amber-600 text-white' : 'text-slate-600 hover:bg-slate-100'}"
    >
      To Do ({stats().pending})
    </button>
    <button
      onclick={() => activeTab = 'submitted'}
      class="px-4 py-2 text-xs font-bold rounded-xl transition {activeTab === 'submitted' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'}"
    >
      Submitted ({stats().submitted})
    </button>
    <button
      onclick={() => activeTab = 'graded'}
      class="px-4 py-2 text-xs font-bold rounded-xl transition {activeTab === 'graded' ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-100'}"
    >
      Graded ({stats().graded})
    </button>
  </div>

  <!-- Assignment Cards -->
  {#if loading}
    <div class="flex justify-center items-center py-20">
      <div class="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  {:else if filteredAssignments().length === 0}
    <div class="bg-white rounded-2xl border border-slate-100 p-12 text-center shadow-sm">
      <div class="w-16 h-16 bg-slate-100 text-slate-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <CheckCircle class="w-8 h-8" />
      </div>
      <h3 class="text-base font-bold text-slate-800 mb-1">No Assignments Found</h3>
      <p class="text-sm text-slate-500">There are no assignments matching your current filter.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each filteredAssignments() as assign (assign.id)}
        {@const sub = getSubmissionForAssignment(assign.id)}
        {@const status = getAssignmentStatus(assign)}

        <div class="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between">
          <div>
            <!-- Header Badges -->
            <div class="flex items-center justify-between gap-2 mb-3">
              <span class="px-2.5 py-1 bg-blue-50 text-blue-700 font-semibold text-xs rounded-lg border border-blue-100">
                {assign.subject_name}
              </span>

              {#if status === 'graded'}
                <span class="px-2.5 py-0.5 bg-emerald-600 text-white font-bold text-xs rounded-md shadow-sm">
                  {sub.marks_obtained} / {assign.max_marks} pts
                </span>
              {:else if status === 'submitted'}
                <span class="px-2 py-0.5 bg-blue-100 text-blue-700 font-semibold text-xs rounded-md">
                  {sub.is_late ? 'Submitted Late' : 'Submitted'}
                </span>
              {:else if status === 'overdue'}
                <span class="px-2 py-0.5 bg-rose-100 text-rose-700 font-semibold text-xs rounded-md flex items-center gap-1">
                  <Clock class="w-3 h-3" /> Overdue
                </span>
              {:else}
                <span class="px-2 py-0.5 bg-amber-100 text-amber-800 font-semibold text-xs rounded-md flex items-center gap-1">
                  <Clock class="w-3 h-3" /> Due Soon
                </span>
              {/if}
            </div>

            <!-- Title & Description -->
            <h3 class="text-base font-bold text-slate-800 mb-1.5">{assign.title}</h3>
            <p class="text-xs text-slate-500 line-clamp-3 mb-4 leading-relaxed">{assign.description || 'No instructions provided.'}</p>

            <!-- Metrics -->
            <div class="space-y-2 border-t border-slate-100 pt-3 text-xs text-slate-600">
              <div class="flex items-center justify-between">
                <span class="flex items-center gap-1.5 text-slate-500">
                  <Calendar class="w-3.5 h-3.5 text-slate-400" /> Deadline:
                </span>
                <span class="font-medium text-slate-700">{formatDateTime(assign.deadline)}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="flex items-center gap-1.5 text-slate-500">
                  <Award class="w-3.5 h-3.5 text-slate-400" /> Max Score:
                </span>
                <span class="font-bold text-blue-600">{assign.max_marks} pts</span>
              </div>
            </div>

            <!-- Feedback preview if graded -->
            {#if status === 'graded' && sub?.feedback_remarks}
              <div class="mt-3 p-2.5 bg-emerald-50/60 border border-emerald-100 rounded-xl text-xs text-emerald-900">
                <div class="font-bold mb-0.5 text-emerald-800">Teacher Remarks:</div>
                <div class="italic text-slate-700 line-clamp-2">"{sub.feedback_remarks}"</div>
              </div>
            {/if}
          </div>

          <!-- Bottom Actions -->
          <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
            {#if assign.attachment}
              <a
                href={assign.attachment}
                target="_blank"
                rel="noreferrer"
                class="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
                title="Download Teacher's Problem Sheet"
              >
                <Paperclip class="w-3.5 h-3.5" /> Material
              </a>
            {:else}
              <div></div>
            {/if}

            <div class="flex items-center gap-2">
              {#if status === 'graded' || status === 'submitted'}
                <button
                  onclick={() => openDetailModal(assign)}
                  class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition"
                >
                  View Submission
                </button>
              {/if}

              {#if status !== 'graded'}
                <button
                  onclick={() => openSubmitModal(assign)}
                  class="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-xs transition shadow-sm"
                >
                  <Upload class="w-3.5 h-3.5" />
                  {sub ? 'Resubmit' : 'Submit Work'}
                </button>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Modal: Submit Deliverable -->
{#if showSubmitModal && activeAssignment}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
        <div>
          <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Upload class="w-5 h-5 text-blue-600" />
            Submit Coursework
          </h3>
          <p class="text-xs text-slate-500">{activeAssignment.title} • {activeAssignment.subject_name}</p>
        </div>
        <button onclick={() => showSubmitModal = false} class="text-slate-400 hover:text-slate-600">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="mb-4 p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs space-y-1">
        <div class="flex justify-between text-slate-600">
          <span>Due Date:</span>
          <span class="font-bold text-slate-800">{formatDateTime(activeAssignment.deadline)}</span>
        </div>
        <div class="flex justify-between text-slate-600">
          <span>Max Marks:</span>
          <span class="font-bold text-blue-600">{activeAssignment.max_marks} pts</span>
        </div>
      </div>

      <form onsubmit={(e) => { e.preventDefault(); handleSubmitAssignment(); }} class="space-y-4">
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Text Response / Solution Links</label>
          <textarea
            bind:value={submissionText}
            rows="4"
            placeholder="Type your essay, code links, or answers here..."
            class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono"
          ></textarea>
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Upload Deliverable File (PDF, DOCX, ZIP, Code)</label>
          <input
            type="file"
            onchange={handleFileChange}
            class="w-full text-sm text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 mt-6">
          <button
            type="button"
            onclick={() => showSubmitModal = false}
            class="px-4 py-2.5 border border-slate-200 text-slate-600 font-semibold rounded-xl text-sm hover:bg-slate-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition shadow-sm disabled:opacity-50 flex items-center gap-2"
          >
            <Upload class="w-4 h-4" />
            {submitting ? 'Submitting...' : 'Upload Submission'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Modal: View Existing Submission -->
{#if showDetailModal && activeAssignment && activeSubmission}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
        <div>
          <h3 class="text-lg font-bold text-slate-800">{activeAssignment.title}</h3>
          <p class="text-xs text-slate-500">Submitted on {formatDateTime(activeSubmission.submitted_at)}</p>
        </div>
        <button onclick={() => showDetailModal = false} class="text-slate-400 hover:text-slate-600">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="space-y-4">
        <!-- Status & Score Ribbon -->
        <div class="p-4 rounded-2xl border {activeSubmission.status === 'Graded' ? 'bg-emerald-50/50 border-emerald-200' : 'bg-blue-50/50 border-blue-200'}">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase text-slate-600">Evaluation Status:</span>
            <span class="font-bold text-xs px-2.5 py-1 rounded-md {activeSubmission.status === 'Graded' ? 'bg-emerald-600 text-white' : 'bg-blue-600 text-white'}">
              {activeSubmission.status}
            </span>
          </div>

          {#if activeSubmission.status === 'Graded'}
            <div class="flex items-center justify-between mt-3 pt-3 border-t border-emerald-200">
              <span class="text-xs font-semibold text-slate-700">Marks Awarded:</span>
              <span class="text-base font-bold text-emerald-700">{activeSubmission.marks_obtained} / {activeAssignment.max_marks} pts</span>
            </div>
            {#if activeSubmission.feedback_remarks}
              <div class="mt-3 pt-3 border-t border-emerald-200">
                <span class="text-xs font-semibold text-slate-700 block mb-1">Instructor Feedback:</span>
                <p class="text-xs text-slate-800 italic bg-white p-3 rounded-xl border border-emerald-100 leading-relaxed">
                  "{activeSubmission.feedback_remarks}"
                </p>
              </div>
            {/if}
          {/if}
        </div>

        <!-- Submitted Text -->
        {#if activeSubmission.submission_text}
          <div>
            <span class="text-xs font-semibold text-slate-600 block mb-1 uppercase">Your Solution / Text:</span>
            <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-800 whitespace-pre-wrap">
              {activeSubmission.submission_text}
            </div>
          </div>
        {/if}

        <!-- Uploaded File -->
        {#if activeSubmission.submission_file}
          <div>
            <span class="text-xs font-semibold text-slate-600 block mb-1 uppercase">Uploaded Deliverable:</span>
            <a
              href={activeSubmission.submission_file}
              target="_blank"
              rel="noreferrer"
              class="flex items-center gap-2 p-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl text-xs font-semibold text-blue-600 transition"
            >
              <Download class="w-4 h-4" />
              Download Submitted File
            </a>
          </div>
        {/if}
      </div>

      <div class="flex justify-end pt-4 border-t border-slate-100 mt-6">
        <button
          onclick={() => showDetailModal = false}
          class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition"
        >
          Close
        </button>
      </div>
    </div>
  </div>
{/if}
