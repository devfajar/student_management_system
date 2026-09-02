<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Award, CheckCircle2, XCircle, BookOpen, FileDown, Printer, AlertCircle, Loader2 } from 'lucide-svelte';

  let results = $state([]);
  let summary = $state({
    total_subjects: 0,
    passed_subjects: 0,
    failed_subjects: 0,
    average_score: 0
  });

  let loading = $state(true);
  let downloadingPdf = $state(false);
  let error = $state('');

  onMount(async () => {
    try {
      const data = await api.getStudentResults();
      results = data.results || [];
      summary = data.summary || summary;
    } catch (err) {
      error = err.message || 'Failed to load examination results';
    } finally {
      loading = false;
    }
  });

  async function handleDownloadPdf() {
    downloadingPdf = true;
    error = '';
    try {
      await api.exportReportCardPdf();
    } catch (err) {
      error = err.message || 'Failed to download PDF report card';
    } finally {
      downloadingPdf = false;
    }
  }

  function handlePrint() {
    window.print();
  }
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <Award class="text-blue-600" size={28} />
        Academic Transcript & Exam Results
      </h1>
      <p class="text-sm text-slate-500 mt-1">Review your official examination scores, grades, and academic performance</p>
    </div>
    <div class="flex items-center gap-2.5 self-start sm:self-auto">
      <button
        class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
        onclick={handleDownloadPdf}
        disabled={downloadingPdf}
      >
        {#if downloadingPdf}
          <Loader2 size={16} class="animate-spin" />
          <span>Generating PDF...</span>
        {:else}
          <FileDown size={16} />
          <span>Download Official PDF</span>
        {/if}
      </button>
      <button
        class="flex items-center gap-2 px-3.5 py-2.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-sm font-medium shadow-sm transition-all"
        onclick={handlePrint}
      >
        <Printer size={16} />
        <span class="hidden sm:inline">Print</span>
      </button>
    </div>
  </div>

  {#if loading}
    <div class="p-12 text-center text-slate-400">
      <Loader2 size={32} class="animate-spin mx-auto mb-2 text-blue-500" />
      <p class="text-sm">Loading your academic records...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-2 text-sm shadow-sm">
      <AlertCircle size={18} />
      <span>{error}</span>
    </div>
  {:else}
    <!-- Summary Metrics -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg">
          {summary.average_score}%
        </div>
        <div>
          <div class="text-xs text-slate-500 font-medium">Average Score</div>
          <div class="text-lg font-bold text-slate-800">{summary.average_score >= 50 ? 'Good Standing' : 'Needs Improvement'}</div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-lg">
          <BookOpen size={24} />
        </div>
        <div>
          <div class="text-2xl font-bold text-slate-800">{summary.total_subjects}</div>
          <div class="text-xs text-slate-500 font-medium">Total Subjects</div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg">
          <CheckCircle2 size={24} />
        </div>
        <div>
          <div class="text-2xl font-bold text-slate-800">{summary.passed_subjects}</div>
          <div class="text-xs text-slate-500 font-medium">Subjects Passed</div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-lg">
          <XCircle size={24} />
        </div>
        <div>
          <div class="text-2xl font-bold text-slate-800">{summary.failed_subjects}</div>
          <div class="text-xs text-slate-500 font-medium">Subjects Failed</div>
        </div>
      </div>
    </div>

    <!-- Results Table -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
        <h2 class="text-base font-bold text-slate-800 flex items-center gap-2">
          <Award class="text-blue-600" size={18} />
          Course Subjects & Performance
        </h2>
        <span class="text-xs text-slate-500 font-medium">{results.length} record{results.length === 1 ? '' : 's'}</span>
      </div>

      {#if results.length === 0}
        <div class="p-12 text-center text-slate-400">
          <Award size={36} class="mx-auto mb-2 opacity-40" />
          <p class="text-sm font-medium">No examination results published yet.</p>
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-slate-50/75 border-b border-slate-200/80 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                <th class="py-3 px-4">Subject</th>
                <th class="py-3 px-4">Course</th>
                <th class="py-3 px-4 text-center">Assignment (50)</th>
                <th class="py-3 px-4 text-center">Exam (50)</th>
                <th class="py-3 px-4 text-center">Total (100)</th>
                <th class="py-3 px-4 text-center">Grade</th>
                <th class="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              {#each results as res}
                <tr class="hover:bg-slate-50/60 transition-colors">
                  <td class="py-3.5 px-4 font-semibold text-slate-800">
                    {res.subject_name}
                  </td>
                  <td class="py-3.5 px-4 text-slate-500 text-xs font-medium">
                    {res.course_name || '-'}
                  </td>
                  <td class="py-3.5 px-4 text-center text-slate-600 font-mono text-xs">
                    {res.subject_assignment_marks}
                  </td>
                  <td class="py-3.5 px-4 text-center text-slate-600 font-mono text-xs">
                    {res.subject_exam_marks}
                  </td>
                  <td class="py-3.5 px-4 text-center font-bold text-slate-800 font-mono">
                    {res.total_marks}
                  </td>
                  <td class="py-3.5 px-4 text-center font-bold">
                    <span class="px-2.5 py-1 rounded-md text-xs {res.grade === 'A+' || res.grade === 'A' ? 'bg-emerald-50 text-emerald-700' : res.grade === 'F' ? 'bg-rose-50 text-rose-700' : 'bg-blue-50 text-blue-700'}">
                      {res.grade}
                    </span>
                  </td>
                  <td class="py-3.5 px-4 text-center">
                    {#if res.status === 'Pass'}
                      <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                        <CheckCircle2 size={12} />
                        Pass
                      </span>
                    {:else}
                      <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/60">
                        <XCircle size={12} />
                        Fail
                      </span>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  @media print {
    :global(aside), :global(header) {
      display: none !important;
    }
  }
</style>

