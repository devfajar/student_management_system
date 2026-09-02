<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import {
    FileText, UploadCloud, CheckCircle2, Clock, XCircle, Trash2,
    Eye, Download, AlertCircle, Loader2, Plus, Info, RefreshCw
  } from 'lucide-svelte';

  let documents = $state([]);
  let loading = $state(true);
  let uploadLoading = $state(false);
  let error = $state('');
  let success = $state('');

  // Upload Form
  let documentName = $state('');
  let documentType = $state('transcript');
  let selectedFile = $state(null);
  let fileInputRef;

  const docTypes = [
    { value: 'transcript', label: 'Academic Transcript' },
    { value: 'id_card', label: 'National ID / Passport' },
    { value: 'certificate', label: 'Diploma / Certificate' },
    { value: 'medical', label: 'Medical Document' },
    { value: 'other', label: 'Other Official Document' }
  ];

  onMount(() => {
    loadDocuments();
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

  function handleFileSelected(e) {
    const file = e.target.files[0];
    if (file) {
      selectedFile = file;
      if (!documentName) {
        // Auto populate title from file name without extension
        documentName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
      }
    }
  }

  async function handleUpload(e) {
    e.preventDefault();
    if (!selectedFile) {
      error = 'Please select a file to upload (PDF, PNG, JPG)';
      return;
    }
    if (!documentName.trim()) {
      error = 'Please enter a document title';
      return;
    }

    uploadLoading = true;
    error = '';
    success = '';

    try {
      const formData = new FormData();
      formData.append('document_name', documentName.trim());
      formData.append('document_type', documentType);
      formData.append('document_file', selectedFile);

      await api.uploadStudentDocument(formData);
      success = 'Document uploaded successfully! It is now pending administrative verification.';
      documentName = '';
      selectedFile = null;
      if (fileInputRef) fileInputRef.value = '';
      await loadDocuments();
    } catch (err) {
      error = err.message || 'Failed to upload document';
    } finally {
      uploadLoading = false;
    }
  }

  async function handleDelete(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;
    try {
      await api.deleteStudentDocument(id);
      success = `Deleted "${name}" successfully.`;
      await loadDocuments();
    } catch (err) {
      error = err.message || 'Failed to delete document';
    }
  }

  // Summary Metrics
  let totalDocs = $derived(documents.length);
  let approvedDocs = $derived(documents.filter(d => d.verification_status === 1).length);
  let pendingDocs = $derived(documents.filter(d => d.verification_status === 0).length);
  let rejectedDocs = $derived(documents.filter(d => d.verification_status === 2).length);
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <FileText class="text-blue-600" size={28} />
        My Academic & Identity Documents
      </h1>
      <p class="text-sm text-slate-500 mt-1">Upload and manage official transcripts, identification, and certificates for verification</p>
    </div>
    <button
      onclick={loadDocuments}
      class="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-sm font-medium shadow-sm transition-all self-start"
    >
      <RefreshCw size={15} class={loading ? 'animate-spin' : ''} />
      <span>Refresh Vault</span>
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
        <FileText size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{totalDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Total Uploaded</div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
        <Clock size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{pendingDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Pending Review</div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
        <CheckCircle2 size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{approvedDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Verified & Approved</div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
        <XCircle size={24} />
      </div>
      <div>
        <div class="text-2xl font-bold text-slate-800">{rejectedDocs}</div>
        <div class="text-xs text-slate-500 font-medium">Requires Revision</div>
      </div>
    </div>
  </div>

  <!-- Upload New Document Card -->
  <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
    <h2 class="text-base font-bold text-slate-800 mb-4 flex items-center gap-2">
      <UploadCloud class="text-blue-600" size={20} />
      Upload Official Document
    </h2>

    <form onsubmit={handleUpload} class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5" for="doc-name">Document Title / Description</label>
          <input
            id="doc-name"
            type="text"
            placeholder="e.g. Official High School Transcript 2025"
            bind:value={documentName}
            class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5" for="doc-type">Document Category</label>
          <select
            id="doc-type"
            bind:value={documentType}
            class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            {#each docTypes as t}
              <option value={t.value}>{t.label}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- File Drop Area -->
      <div class="border-2 border-dashed border-slate-200 hover:border-blue-400 bg-slate-50/50 hover:bg-blue-50/30 rounded-2xl p-6 text-center transition-all">
        <input
          bind:this={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
          class="hidden"
          id="doc-file-input"
          onchange={handleFileSelected}
        />
        <label for="doc-file-input" class="cursor-pointer flex flex-col items-center justify-center gap-2">
          <div class="w-12 h-12 rounded-full bg-blue-100/80 text-blue-600 flex items-center justify-center shadow-inner">
            <UploadCloud size={24} />
          </div>
          {#if selectedFile}
            <div class="text-sm font-semibold text-blue-700">{selectedFile.name}</div>
            <div class="text-xs text-slate-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB &bull; Click to choose another file</div>
          {:else}
            <div class="text-sm font-semibold text-slate-700">Click to select file from your device</div>
            <div class="text-xs text-slate-400">Supports PDF, PNG, JPG, DOCX (Max 10MB)</div>
          {/if}
        </label>
      </div>

      <div class="flex justify-end">
        <button
          type="submit"
          class="flex items-center justify-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
          disabled={uploadLoading}
        >
          {#if uploadLoading}
            <Loader2 size={16} class="animate-spin" />
            <span>Uploading Document...</span>
          {:else}
            <Plus size={16} />
            <span>Submit for Verification</span>
          {/if}
        </button>
      </div>
    </form>
  </div>

  <!-- Documents Vault List -->
  <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
    <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
      <h2 class="text-base font-bold text-slate-800">Your Document Vault</h2>
      <span class="text-xs text-slate-500 font-medium">{documents.length} document{documents.length === 1 ? '' : 's'} recorded</span>
    </div>

    {#if loading}
      <div class="p-12 text-center text-slate-400">
        <Loader2 size={32} class="animate-spin mx-auto mb-2 text-blue-500" />
        <p class="text-sm">Loading your vault documents...</p>
      </div>
    {:else if documents.length === 0}
      <div class="p-12 text-center">
        <div class="w-16 h-16 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
          <FileText size={28} />
        </div>
        <h3 class="text-base font-bold text-slate-700 mb-1">No Documents Uploaded Yet</h3>
        <p class="text-xs text-slate-500 max-w-sm mx-auto">Upload your academic transcripts, national ID, or certificates using the form above to verify your student profile.</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-200/80 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-4">Document Title</th>
              <th class="py-3 px-4">Category</th>
              <th class="py-3 px-4">Uploaded Date</th>
              <th class="py-3 px-4">Verification Status</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            {#each documents as doc}
              <tr class="hover:bg-slate-50/60 transition-colors">
                <td class="py-3.5 px-4 font-semibold text-slate-800">
                  <div class="flex items-center gap-2.5">
                    <div class="p-2 rounded-lg bg-blue-50 text-blue-600">
                      <FileText size={18} />
                    </div>
                    <div>
                      <div>{doc.document_name}</div>
                      {#if doc.rejection_reason && doc.verification_status === 2}
                        <div class="mt-1 text-xs text-rose-600 bg-rose-50/80 px-2.5 py-1 rounded-md border border-rose-100 font-normal flex items-center gap-1.5">
                          <AlertCircle size={13} />
                          <span><strong>Feedback:</strong> {doc.rejection_reason}</span>
                        </div>
                      {/if}
                    </div>
                  </div>
                </td>
                <td class="py-3.5 px-4 text-slate-600 text-xs font-medium">
                  <span class="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700">
                    {doc.type_display || doc.document_type}
                  </span>
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
                      Pending Verification
                    </span>
                  {/if}
                </td>
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    {#if doc.document_file}
                      <a
                        href={doc.document_file}
                        target="_blank"
                        rel="noreferrer"
                        class="p-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-all"
                        title="View / Download Document"
                      >
                        <Eye size={16} />
                      </a>
                    {/if}
                    <button
                      onclick={() => handleDelete(doc.id, doc.document_name)}
                      class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                      title="Delete Document"
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
