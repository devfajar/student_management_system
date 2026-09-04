<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';

  let loading = true;
  let error = '';
  let salaryInfo = null;
  let payrolls = [];

  const months = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  onMount(async () => {
    await loadData();
  });

  async function loadData() {
    loading = true;
    error = '';
    try {
      const [salRes, payRes] = await Promise.allSettled([
        api.getMySalary(),
        api.getStaffPayrolls()
      ]);

      if (salRes.status === 'fulfilled') {
        salaryInfo = salRes.value;
      }
      if (payRes.status === 'fulfilled') {
        payrolls = Array.isArray(payRes.value) ? payRes.value : (payRes.value?.results || []);
      }
    } catch (e) {
      error = e.message || 'Failed to load payslip data';
    } finally {
      loading = false;
    }
  }

  async function downloadPayslip(p) {
    try {
      const monthName = months[p.payroll_month] || p.payroll_month;
      await api.exportPayslipPdf(p.id, `Payslip_${monthName}_${p.payroll_year}.pdf`);
    } catch (e) {
      error = 'Failed to download payslip PDF';
    }
  }
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div>
    <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
      <span>💵</span> My Salary & Payslips
    </h1>
    <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
      View your monthly compensation package, past salary disbursements, and download official PDF payslips.
    </p>
  </div>

  {#if error}
    <div class="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-lg text-rose-800 dark:text-rose-200 text-sm flex items-center gap-2">
      <span>⚠️</span> {error}
    </div>
  {/if}

  {#if loading}
    <div class="p-12 text-center text-slate-500">Loading your compensation details...</div>
  {:else}
    <!-- Active Salary Package Card -->
    {#if salaryInfo}
      <div class="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-md border border-indigo-800/40">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="text-xs font-semibold text-indigo-300 uppercase tracking-wider">Faculty Package Tier</div>
            <h2 class="text-xl font-extrabold mt-1">{salaryInfo.designation}</h2>
            <p class="text-xs text-indigo-200/80 mt-0.5">Effective Date: {salaryInfo.effective_date || 'Current Academic Term'}</p>
          </div>
          <div class="flex flex-wrap items-center gap-6">
            <div>
              <div class="text-xs text-indigo-300 font-medium">Base Salary</div>
              <div class="text-lg font-bold font-mono mt-0.5">${parseFloat(salaryInfo.base_salary || 0).toFixed(2)}</div>
            </div>
            <div>
              <div class="text-xs text-indigo-300 font-medium">Standard Allowance</div>
              <div class="text-lg font-bold font-mono mt-0.5">${parseFloat(salaryInfo.allowance || 0).toFixed(2)}</div>
            </div>
            <div class="border-l border-indigo-700/60 pl-6">
              <div class="text-xs text-indigo-200 font-semibold">Gross Monthly</div>
              <div class="text-2xl font-extrabold font-mono text-emerald-400 mt-0.5">${parseFloat(salaryInfo.total_monthly_gross || 0).toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Payslips History Ledger -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
      <div class="p-5 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <div>
          <h3 class="font-bold text-slate-800 dark:text-slate-100">Disbursement History</h3>
          <p class="text-xs text-slate-500 mt-0.5">Official monthly payslips issued by the institution</p>
        </div>
        <span class="text-xs font-semibold px-2.5 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full">
          {payrolls.length} Records
        </span>
      </div>

      {#if payrolls.length === 0}
        <div class="p-12 text-center">
          <span class="text-4xl">📄</span>
          <h4 class="text-base font-semibold text-slate-700 dark:text-slate-300 mt-3">No payslips issued yet</h4>
          <p class="text-xs text-slate-500 mt-1">Your monthly payroll statements will appear here once disbursed by Administration.</p>
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-slate-50 dark:bg-slate-900/60 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-5 py-3.5">Period</th>
                <th class="px-4 py-3.5 text-right">Base</th>
                <th class="px-4 py-3.5 text-right">Allowances</th>
                <th class="px-4 py-3.5 text-right">Bonus</th>
                <th class="px-4 py-3.5 text-right">Deductions</th>
                <th class="px-4 py-3.5 text-right font-bold">Net Salary</th>
                <th class="px-4 py-3.5 text-center">Status</th>
                <th class="px-4 py-3.5">Disbursement Date</th>
                <th class="px-5 py-3.5 text-right">Official Document</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
              {#each payrolls as p}
                <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-700/30 transition-colors">
                  <td class="px-5 py-4 font-semibold text-slate-800 dark:text-slate-200">
                    {months[p.payroll_month] || p.payroll_month} {p.payroll_year}
                  </td>
                  <td class="px-4 py-4 text-right font-mono text-slate-600 dark:text-slate-300">${parseFloat(p.basic_salary).toFixed(2)}</td>
                  <td class="px-4 py-4 text-right font-mono text-slate-600 dark:text-slate-300">${parseFloat(p.allowances).toFixed(2)}</td>
                  <td class="px-4 py-4 text-right font-mono text-emerald-600 dark:text-emerald-400">+${parseFloat(p.bonus).toFixed(2)}</td>
                  <td class="px-4 py-4 text-right font-mono text-rose-600 dark:text-rose-400">-${parseFloat(p.deductions).toFixed(2)}</td>
                  <td class="px-4 py-4 text-right font-mono font-bold text-slate-900 dark:text-white">${parseFloat(p.net_salary).toFixed(2)}</td>
                  <td class="px-4 py-4 text-center">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold {p.payment_status === 'Paid' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'}">
                      {p.payment_status}
                    </span>
                  </td>
                  <td class="px-4 py-4 text-slate-600 dark:text-slate-400 text-xs">
                    {#if p.payment_date}
                      <div>{p.payment_date}</div>
                      <div class="text-slate-400">{p.payment_method}</div>
                    {:else}
                      <span class="text-amber-500 italic">Pending Transfer</span>
                    {/if}
                  </td>
                  <td class="px-5 py-4 text-right">
                    <button
                      on:click={() => downloadPayslip(p)}
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 text-xs font-semibold rounded-lg transition-all"
                    >
                      <span>📥</span> Download PDF
                    </button>
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
