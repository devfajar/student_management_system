<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import {
    FileCheck, CheckCircle2, Clock, XCircle, Trash2,
    Eye, Download, AlertCircle, Loader2, Search, Filter,
    RefreshCw, User, ExternalLink
  } from 'lucide-svelte';
  import Modal from '../../components/Modal.svelte';

  let documents = $state([]);
  let courses = $state([]);
  let loading = $state(true);
  let actionLoading = $state(false);
  let error = $state('');
  let success = $state('');

  // Filters
  let searchQuery = $state('');
  let statusFilter = $state('all');
  let courseFilter = $state('all');

  // Reject Modal
  let showRejectModal = $state(false);
  let rejectingDoc = $state(null);
  let rejectionReason = $state('');

  onMount(async () => {
    await Promise.all([loadDocuments(), loadCourses()]);
  });

  async function loadDocuments() {
    loading = true;
    error = '';
    try {
      documents = await api.getStudentDocuments();
    } catch (err) {
      error = err.message || 'Failed to load documents';
    } finally {
      loading = false;
    }
  }

  async function loadCourses() {
    try {
      courses = await api.getCoursesList();
    } catch (err) {
      console.error('Failed to load courses', err);
    }
  }

  async function handleApprove(doc) {
    actionLoading = true;
    error = '';
    success = '';
    try {
      await api.verifyStudentDocument(doc.id, 1);
      success = `Approved document "${doc.document_name}" for ${doc.student_name || doc.student_username}.`;
      await loadDocuments();
    } catch (err) {
      error = err.message || 'Failed to approve document';
    } finally {
      actionLoading = false;
    }
  }

  function openRejectModal(doc) {
    rejectingDoc = doc;
    rejectionReason = '';
    showRejectModal = true;
  }

  async function handleRejectSubmit(e) {
    e.preventDefault();
    if (!rejectingDoc) return;
    if (!rejectionReason.trim()) {
      alert('Please provide a reason for rejecting this document so the student can rectify it.');
      return;
    }

    actionLoading = true;
    error = '';
    success = '';
    try {
      await api.verifyStudentDocument(rejectingDoc.id, 2, rejectionReason.trim());
      success = `Rejected document "${rejectingDoc.document_name}" with feedback note.`;
      showRejectModal = false;
      rejectingDoc = null;
      await loadDocuments();
    } catch (err) {
      error = err.message || 'Failed to reject document';
    } finally {
      actionLoading = false;
    }
  }

  async function handleDelete(doc) {
    if (!confirm(`Are you sure you want to permanently delete "${doc.document_name}"?`)) return;
    try {
      await api.deleteStudentDocument(doc.id);
      success = `Deleted "${doc.document_name}" successfully.`;
      await loadDocuments();
    } catch (err) {
      error = err.message || 'Failed to delete document';
    }
  }

  // Filtered list
  let filteredDocuments = $derived(
    documents.filter(doc => {
      const matchesSearch =
        (doc.document_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (doc.student_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (doc.student_username || '').toLowerCase().includes(searchQuery.toLowerCase());

      const matchesStatus =
        statusFilter === 'all' || String(doc.verification_status) === statusFilter;

      const matchesCourse =
        courseFilter === 'all' || doc.course_name === courseFilter;

      return matchesSearch && matchesStatus && matchesCourse;
    })
  );

  // Summary Metrics
  let totalDocs = $derived(documents.length);
  let pendingDocs = $derived(documents.filter(d => d.verification_status === 0).length);
  let approvedDocs = $derived(documents.filter(d => d.verification_status === 1).length);
  let rejectedDocs = $derived(documents.filter(d => d.verification_status === 2).length);
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <FileCheck class="text-blue-600" size={28} />
        Student Document Verification Queue
      </h1>
      <p class="text-sm text-slate-500 mt-1">Review, verify, and manage uploaded official transcripts, identity proofs, and credentials</p>
    </div>
    <button
      onclick={loadDocuments}
      class="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-sm font-medium shadow-sm transition-all self-start"
    >
      <RefreshCw size={15} class={loading ? 'animate-spin' : ''} />
      <span>Refresh Queue</span>
    </button>
  </div>

  <!-- Alerts -->
  {#if success}
    <div class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl flex items-center justify-between text-sm shadow-sm">
      <div class="flex items-center gap-2">
        <CheckCircle2 size={18} />
        <span>{success}</span>
      </div>
      <button onclick={() => success = ''} class="text-emerald-500 hover:text-emerald-700 text-xs font-bold">&times;</button>
    </div>
  {/if}

  {#if error}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center justify-between text-sm shadow-sm">
      <div class="flex items-center gap-2">
        <AlertCircle size={18} />
        <span>{error}</span>
      </div>
      <button onclick={() => error = ''} class="text-red-500 hover:text-red-700 text-xs font-bold">&times;</button>
    </div>
  {/if}

  <!-- KPI Overview Cards -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
        <FileCheck size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{totalDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Total Documents</div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
        <Clock size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{pendingDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Needs Verification</div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
        <CheckCircle2 size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{approvedDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Approved</div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
        <XCircle size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{rejectedDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Rejected / Revisions</div>
      </div>
    </div>
  </div>

  <!-- Filters Bar -->
  <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
    <div class="relative w-full md:w-80">
      <Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <input
        type="text"
        placeholder="Search student or document..."
        bind:value={searchQuery}
        class="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
      />
    </div>

    <div class="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
      <select
        bind:value={statusFilter}
        class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
      >
        <option value="all">All Statuses</option>
        <option value="0">Pending Review</option>
        <option value="1">Approved</option>
        <option value="2">Rejected</option>
      </select>

      <select
        bind:value={courseFilter}
        class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
      >
        <option value="all">All Courses</option>
        {#each courses as c}
          <option value={c.course_name}>{c.course_name}</option>
        {/each}
      </select>
    </div>
  </div>

  <!-- Documents Table -->
  <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
    {#if loading}
      <div class="p-12 text-center text-slate-400">
        <Loader2 size={32} class="animate-spin mx-auto mb-2 text-blue-500" />
        <p class="text-sm">Loading document submissions...</p>
      </div>
    {:else if filteredDocuments.length === 0}
      <div class="p-12 text-center text-slate-400">
        <FileCheck size={36} class="mx-auto mb-2 opacity-40" />
        <p class="text-sm font-medium">No student documents match your selected criteria.</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-200/80 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-4">Student</th>
              <th class="py-3 px-4">Course</th>
              <th class="py-3 px-4">Document Details</th>
              <th class="py-3 px-4">Submission Date</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4 text-right">Verification Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            {#each filteredDocuments as doc}
              <tr class="hover:bg-slate-50/60 transition-colors">
                <td class="py-3.5 px-4">
                  <div class="font-bold text-slate-800">{doc.student_name}</div>
                  <div class="text-xs text-slate-500 font-mono">@{doc.student_username}</div>
                </td>
                <td class="py-3.5 px-4 text-slate-600 text-xs font-medium">
                  {doc.course_name || '—'}
                </td>
                <td class="py-3.5 px-4">
                  <div class="font-semibold text-slate-800">{doc.document_name}</div>
                  <div class="mt-0.5 inline-block px-2 py-0.5 rounded text-[11px] bg-slate-100 text-slate-600 font-medium">
                    {doc.type_display || doc.document_type}
                  </div>
                  {#if doc.rejection_reason && doc.verification_status === 2}
                    <div class="mt-1 text-xs text-rose-600 bg-rose-50 p-2 rounded-md border border-rose-100">
                      <strong>Rejection Note:</strong> {doc.rejection_reason}
                    </div>
                  {/if}
                </td>
                <td class="py-3.5 px-4 text-slate-500 text-xs">
                  {new Date(doc.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                </td>
                <td class="py-3.5 px-4">
                  {#if doc.verification_status === 1}
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                      <CheckCircle2 size={13} />
                      Approved
                    </span>
                  {:else if doc.verification_status === 2}
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/60">
                      <XCircle size={13} />
                      Rejected
                    </span>
                  {:else}
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200/60">
                      <Clock size={13} />
                      Pending Review
                    </span>
                  {/if}
                </td>
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    {#if doc.document_file}
                      <a
                        href={doc.document_file}
                        target="_blank"
                        rel="noreferrer"
                        class="p-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-all"
                        title="View Full File"
                      >
                        <ExternalLink size={16} />
                      </a>
                    {/if}

                    {#if doc.verification_status !== 1}
                      <button
                        onclick={() => handleApprove(doc)}
                        class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1"
                        disabled={actionLoading}
                        title="Approve Document"
                      >
                        <CheckCircle2 size={13} />
                        <span>Approve</span>
                      </button>
                    {/if}

                    {#if doc.verification_status !== 2}
                      <button
                        onclick={() => openRejectModal(doc)}
                        class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-lg text-xs font-semibold transition-all flex items-center gap-1"
                        disabled={actionLoading}
                        title="Reject Document"
                      >
                        <XCircle size={13} />
                        <span>Reject</span>
                      </button>
                    {/if}

                    <button
                      onclick={() => handleDelete(doc)}
                      class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                      title="Delete Record"
                    >
                      <Trash2 size={16} />
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

<!-- Reject Modal -->
<Modal show={showRejectModal} title="Reject Document Submission" onclose={() => showRejectModal = false}>
  {#if rejectingDoc}
    <form onsubmit={handleRejectSubmit} class="space-y-4">
      <div class="bg-amber-50 border border-amber-200 p-3.5 rounded-xl text-xs text-amber-800">
        You are rejecting <strong>"{rejectingDoc.document_name}"</strong> submitted by <strong>{rejectingDoc.student_name}</strong>. Please provide a clear explanation so the student can re-upload a compliant file.
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Feedback / Rejection Reason</label>
        <textarea
          rows="3"
          placeholder="e.g. Document image is blurry and date of birth is illegible. Please re-upload a clean high-resolution color scan."
          bind:value={rejectionReason}
          class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500"
          required
        ></textarea>
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <button
          type="button"
          class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-medium transition-all"
          onclick={() => showRejectModal = false}
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-5 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
          disabled={actionLoading}
        >
          Confirm Rejection
        </button>
      </div>
    </form>
  {/if}
</Modal>
