<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';

  let activeTab = 'payroll'; // 'payroll' or 'salary_structures'
  let loading = true;
  let error = '';
  let successMsg = '';

  // Stats
  let stats = {
    total_records: 0,
    total_disbursed: 0,
    pending_payouts: 0,
    paid_count: 0,
    pending_count: 0,
    total_staff: 0,
    configured_salaries: 0
  };

  // Staff and Salaries
  let staffList = [];
  let salaryList = [];

  // Payrolls
  let payrollList = [];
  let selectedMonth = new Date().getMonth() + 1; // 1-12
  let selectedYear = new Date().getFullYear();
  let statusFilter = '';
  let searchQuery = '';

  // Modals
  let showSalaryModal = false;
  let editingSalary = null;
  let salaryForm = {
    staff: '',
    designation: 'Lecturer',
    base_salary: '',
    allowance: '',
    tax_percentage: '0.00',
    effective_date: '',
    is_active: true
  };

  let showMarkPaidModal = false;
  let targetPayroll = null;
  let markPaidForm = {
    payment_method: 'Bank Transfer',
    payment_date: new Date().toISOString().split('T')[0],
    remarks: ''
  };

  let showBatchModal = false;
  let batchForm = {
    payroll_month: selectedMonth,
    payroll_year: selectedYear
  };

  let isSubmitting = false;

  const months = [
    { value: 1, name: 'January' },
    { value: 2, name: 'February' },
    { value: 3, name: 'March' },
    { value: 4, name: 'April' },
    { value: 5, name: 'May' },
    { value: 6, name: 'June' },
    { value: 7, name: 'July' },
    { value: 8, name: 'August' },
    { value: 9, name: 'September' },
    { value: 10, name: 'October' },
    { value: 11, name: 'November' },
    { value: 12, name: 'December' }
  ];

  const currentYear = new Date().getFullYear();
  const years = [currentYear - 1, currentYear, currentYear + 1];

  onMount(async () => {
    await loadInitialData();
  });

  async function loadInitialData() {
    loading = true;
    error = '';
    try {
      const [staffRes, salRes] = await Promise.all([
        api.getStaff(),
        api.getStaffSalaries()
      ]);
      staffList = staffRes || [];
      salaryList = salRes || [];
      await Promise.all([loadPayrolls(), loadStats()]);
    } catch (err) {
      error = err.message || 'Failed to load payroll records';
    } finally {
      loading = false;
    }
  }

  async function loadStats() {
    try {
      const res = await api.getPayrollStats({ month: selectedMonth, year: selectedYear });
      stats = res;
    } catch (e) {
      console.error('Failed to load stats', e);
    }
  }

  async function loadPayrolls() {
    try {
      const params = {
        month: selectedMonth,
        year: selectedYear
      };
      if (statusFilter) params.payment_status = statusFilter;
      if (searchQuery) params.search = searchQuery;
      payrollList = await api.getStaffPayrolls(params);
    } catch (err) {
      error = err.message || 'Failed to fetch payroll list';
    }
  }

  function handleFilterChange() {
    loadPayrolls();
    loadStats();
  }

  // Salary Tier Configuration
  function openAddSalaryModal(staff = null) {
    editingSalary = null;
    salaryForm = {
      staff: staff ? staff.id : (staffList[0]?.id || ''),
      designation: 'Lecturer',
      base_salary: '5000.00',
      allowance: '500.00',
      tax_percentage: '5.00',
      effective_date: new Date().toISOString().split('T')[0],
      is_active: true
    };
    showSalaryModal = true;
  }

  function openEditSalaryModal(sal) {
    editingSalary = sal;
    salaryForm = {
      staff: sal.staff,
      designation: sal.designation,
      base_salary: sal.base_salary,
      allowance: sal.allowance,
      tax_percentage: sal.tax_percentage,
      effective_date: sal.effective_date || '',
      is_active: sal.is_active
    };
    showSalaryModal = true;
  }

  async function saveSalaryStructure() {
    isSubmitting = true;
    error = '';
    try {
      if (editingSalary) {
        await api.updateStaffSalary(editingSalary.id, salaryForm);
        successMsg = 'Salary structure updated successfully!';
      } else {
        await api.createStaffSalary(salaryForm);
        successMsg = 'Salary structure created successfully!';
      }
      showSalaryModal = false;
      salaryList = await api.getStaffSalaries();
      await loadStats();
      setTimeout(() => (successMsg = ''), 3500);
    } catch (err) {
      error = err.message || 'Failed to save salary tier configuration';
    } finally {
      isSubmitting = false;
    }
  }

  // Batch Payroll Generation
  async function runBatchGeneration() {
    isSubmitting = true;
    error = '';
    try {
      const res = await api.batchGeneratePayroll({
        payroll_month: batchForm.payroll_month,
        payroll_year: batchForm.payroll_year
      });
      successMsg = res.message || `Generated ${res.generated_count} payroll records!`;
      showBatchModal = false;
      selectedMonth = batchForm.payroll_month;
      selectedYear = batchForm.payroll_year;
      await handleFilterChange();
      setTimeout(() => (successMsg = ''), 4000);
    } catch (err) {
      error = err.message || 'Batch payroll generation failed';
    } finally {
      isSubmitting = false;
    }
  }

  // Mark Payroll as Paid
  function openMarkPaidModal(payroll) {
    targetPayroll = payroll;
    markPaidForm = {
      payment_method: 'Bank Transfer',
      payment_date: new Date().toISOString().split('T')[0],
      remarks: ''
    };
    showMarkPaidModal = true;
  }

  async function submitMarkPaid() {
    if (!targetPayroll) return;
    isSubmitting = true;
    error = '';
    try {
      await api.markPayrollPaid(targetPayroll.id, markPaidForm);
      successMsg = `Payroll for ${targetPayroll.staff_name} marked as Paid!`;
      showMarkPaidModal = false;
      await handleFilterChange();
      setTimeout(() => (successMsg = ''), 3500);
    } catch (err) {
      error = err.message || 'Failed to update payment status';
    } finally {
      isSubmitting = false;
    }
  }

  // Export handlers
  async function downloadPayslip(payroll) {
    try {
      await api.exportPayslipPdf(payroll.id, `Payslip_${payroll.staff_username}_${payroll.payroll_month}_${payroll.payroll_year}.pdf`);
    } catch (err) {
      error = 'Failed to download payslip PDF';
    }
  }

  async function exportExcel() {
    try {
      await api.exportPayrollExcel(
        { month: selectedMonth, year: selectedYear, search: searchQuery },
        `Payroll_${selectedMonth}_${selectedYear}.xlsx`
      );
    } catch (e) {
      error = 'Failed to export payroll Excel spreadsheet';
    }
  }

  async function exportCsv() {
    try {
      await api.exportPayrollCsv(
        { month: selectedMonth, year: selectedYear, search: searchQuery },
        `Payroll_${selectedMonth}_${selectedYear}.csv`
      );
    } catch (e) {
      error = 'Failed to export payroll CSV';
    }
  }
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
        <span>💼</span> Staff Salary & Payroll Management
      </h1>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
        Configure compensation tiers, process monthly payroll batches, and disburse verifiable PDF payslips.
      </p>
    </div>
    <div class="flex flex-wrap items-center gap-2">
      <button
        on:click={() => { batchForm.payroll_month = selectedMonth; batchForm.payroll_year = selectedYear; showBatchModal = true; }}
        class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-sm transition-all"
      >
        <span>⚡</span> Run Monthly Batch
      </button>
      <button
        on:click={exportExcel}
        class="inline-flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg shadow-sm transition-all"
      >
        <span>📊</span> Export Excel
      </button>
      <button
        on:click={exportCsv}
        class="inline-flex items-center gap-2 px-3.5 py-2 bg-slate-700 hover:bg-slate-800 text-white text-sm font-medium rounded-lg shadow-sm transition-all"
      >
        <span>📄</span> Export CSV
      </button>
    </div>
  </div>

  <!-- Alert Notifications -->
  {#if successMsg}
    <div class="p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-lg text-emerald-800 dark:text-emerald-200 text-sm flex items-center gap-2">
      <span>✅</span> {successMsg}
    </div>
  {/if}
  {#if error}
    <div class="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-lg text-rose-800 dark:text-rose-200 text-sm flex items-center gap-2">
      <span>⚠️</span> {error}
    </div>
  {/if}

  <!-- KPI Overview Cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Total Disbursed ({months[selectedMonth - 1]?.name})</div>
      <div class="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-2">
        ${stats.total_disbursed?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
      <div class="text-xs text-slate-500 mt-1">{stats.paid_count || 0} staff paid</div>
    </div>
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Pending Payouts</div>
      <div class="text-2xl font-extrabold text-amber-600 dark:text-amber-400 mt-2">
        ${stats.pending_payouts?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
      <div class="text-xs text-slate-500 mt-1">{stats.pending_count || 0} payments awaiting disbursement</div>
    </div>
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Configured Staff Tiers</div>
      <div class="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-2">
        {stats.configured_salaries || 0} <span class="text-sm font-normal text-slate-400">/ {stats.total_staff || 0}</span>
      </div>
      <div class="text-xs text-slate-500 mt-1">Active faculty salary structures</div>
    </div>
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Ledger Records</div>
      <div class="text-2xl font-extrabold text-slate-700 dark:text-slate-300 mt-2">
        {stats.total_records || 0}
      </div>
      <div class="text-xs text-slate-500 mt-1">In selected month & year</div>
    </div>
  </div>

  <!-- Tab Navigation -->
  <div class="border-b border-slate-200 dark:border-slate-700 flex gap-6">
    <button
      class="pb-3 text-sm font-semibold transition-colors border-b-2 flex items-center gap-2 {activeTab === 'payroll' ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}"
      on:click={() => (activeTab = 'payroll')}
    >
      <span>📑</span> Monthly Payroll Ledger
    </button>
    <button
      class="pb-3 text-sm font-semibold transition-colors border-b-2 flex items-center gap-2 {activeTab === 'salary_structures' ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}"
      on:click={() => (activeTab = 'salary_structures')}
    >
      <span>⚙️</span> Salary Tiers & Designations
    </button>
  </div>

  <!-- TAB 1: Monthly Payroll Ledger -->
  {#if activeTab === 'payroll'}
    <div class="space-y-4">
      <!-- Filter Toolbar -->
      <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div class="flex flex-wrap items-center gap-3">
          <div>
            <label for="month-select" class="block text-xs font-semibold text-slate-500 mb-1">Month</label>
            <select
              id="month-select"
              bind:value={selectedMonth}
              on:change={handleFilterChange}
              class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            >
              {#each months as m}
                <option value={m.value}>{m.name}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="year-select" class="block text-xs font-semibold text-slate-500 mb-1">Year</label>
            <select
              id="year-select"
              bind:value={selectedYear}
              on:change={handleFilterChange}
              class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            >
              {#each years as y}
                <option value={y}>{y}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="status-select" class="block text-xs font-semibold text-slate-500 mb-1">Status</label>
            <select
              id="status-select"
              bind:value={statusFilter}
              on:change={handleFilterChange}
              class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            >
              <option value="">All Statuses</option>
              <option value="Paid">Paid</option>
              <option value="Pending">Pending</option>
              <option value="Processing">Processing</option>
            </select>
          </div>
        </div>

        <div class="flex-1 max-w-xs">
          <label for="search-input" class="block text-xs font-semibold text-slate-500 mb-1">Search Staff</label>
          <input
            id="search-input"
            type="text"
            bind:value={searchQuery}
            on:input={handleFilterChange}
            placeholder="Search by name or username..."
            class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
          />
        </div>
      </div>

      <!-- Payroll Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        {#if loading}
          <div class="p-8 text-center text-slate-500">Loading payroll ledger...</div>
        {:else if payrollList.length === 0}
          <div class="p-12 text-center">
            <span class="text-4xl">📂</span>
            <h3 class="text-base font-semibold text-slate-700 dark:text-slate-300 mt-3">No payroll records found</h3>
            <p class="text-sm text-slate-500 mt-1">No payroll entries recorded for {months[selectedMonth - 1]?.name} {selectedYear}.</p>
            <button
              on:click={() => { batchForm.payroll_month = selectedMonth; batchForm.payroll_year = selectedYear; showBatchModal = true; }}
              class="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg"
            >
              Generate Records for this Month
            </button>
          </div>
        {:else}
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 dark:bg-slate-900/60 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th class="px-5 py-3.5">Staff Employee</th>
                  <th class="px-4 py-3.5">Designation</th>
                  <th class="px-4 py-3.5 text-right">Basic</th>
                  <th class="px-4 py-3.5 text-right">Allowances</th>
                  <th class="px-4 py-3.5 text-right">Bonus</th>
                  <th class="px-4 py-3.5 text-right">Deductions</th>
                  <th class="px-4 py-3.5 text-right font-bold">Net Salary</th>
                  <th class="px-4 py-3.5 text-center">Status</th>
                  <th class="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
                {#each payrollList as p}
                  <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-700/30 transition-colors">
                    <td class="px-5 py-4">
                      <div class="font-semibold text-slate-800 dark:text-slate-100">{p.staff_name}</div>
                      <div class="text-xs text-slate-500">@{p.staff_username} &bull; {p.staff_email}</div>
                    </td>
                    <td class="px-4 py-4 text-slate-600 dark:text-slate-300">{p.designation}</td>
                    <td class="px-4 py-4 text-right text-slate-700 dark:text-slate-300 font-mono">${parseFloat(p.basic_salary).toFixed(2)}</td>
                    <td class="px-4 py-4 text-right text-slate-700 dark:text-slate-300 font-mono">${parseFloat(p.allowances).toFixed(2)}</td>
                    <td class="px-4 py-4 text-right text-emerald-600 dark:text-emerald-400 font-mono">+${parseFloat(p.bonus).toFixed(2)}</td>
                    <td class="px-4 py-4 text-right text-rose-600 dark:text-rose-400 font-mono">-${parseFloat(p.deductions).toFixed(2)}</td>
                    <td class="px-4 py-4 text-right font-bold text-slate-900 dark:text-white font-mono">${parseFloat(p.net_salary).toFixed(2)}</td>
                    <td class="px-4 py-4 text-center">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold {p.payment_status === 'Paid' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : p.payment_status === 'Processing' ? 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'}">
                        {p.payment_status}
                      </span>
                    </td>
                    <td class="px-5 py-4 text-right whitespace-nowrap space-x-2">
                      {#if p.payment_status !== 'Paid'}
                        <button
                          on:click={() => openMarkPaidModal(p)}
                          class="px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium rounded-md shadow-sm transition-all"
                          title="Disburse / Mark as Paid"
                        >
                          Disburse
                        </button>
                      {/if}
                      <button
                        on:click={() => downloadPayslip(p)}
                        class="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-xs font-medium rounded-md transition-all"
                        title="Download PDF Payslip"
                      >
                        PDF
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- TAB 2: Salary Tiers & Designations -->
  {#if activeTab === 'salary_structures'}
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-slate-500">Manage base salary packages, standard allowances, and tax withholding percentages for academic staff.</p>
        <button
          on:click={() => openAddSalaryModal()}
          class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-sm transition-all"
        >
          <span>➕</span> Add Salary Tier
        </button>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-slate-50 dark:bg-slate-900/60 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-5 py-3.5">Staff Member</th>
                <th class="px-4 py-3.5">Designation</th>
                <th class="px-4 py-3.5 text-right">Base Salary</th>
                <th class="px-4 py-3.5 text-right">Monthly Allowance</th>
                <th class="px-4 py-3.5 text-right">Gross Monthly</th>
                <th class="px-4 py-3.5 text-right">Tax (%)</th>
                <th class="px-4 py-3.5 text-center">Status</th>
                <th class="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
              {#each salaryList as sal}
                <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-700/30 transition-colors">
                  <td class="px-5 py-4">
                    <div class="font-semibold text-slate-800 dark:text-slate-100">{sal.staff_name}</div>
                    <div class="text-xs text-slate-500">@{sal.staff_username} &bull; {sal.staff_email}</div>
                  </td>
                  <td class="px-4 py-4 font-medium text-slate-700 dark:text-slate-300">{sal.designation}</td>
                  <td class="px-4 py-4 text-right font-mono text-slate-800 dark:text-slate-200">${parseFloat(sal.base_salary).toFixed(2)}</td>
                  <td class="px-4 py-4 text-right font-mono text-slate-800 dark:text-slate-200">${parseFloat(sal.allowance).toFixed(2)}</td>
                  <td class="px-4 py-4 text-right font-mono font-bold text-indigo-600 dark:text-indigo-400">${parseFloat(sal.total_monthly_gross).toFixed(2)}</td>
                  <td class="px-4 py-4 text-right font-mono text-slate-600 dark:text-slate-400">{sal.tax_percentage}%</td>
                  <td class="px-4 py-4 text-center">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {sal.is_active ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'}">
                      {sal.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td class="px-5 py-4 text-right whitespace-nowrap">
                    <button
                      on:click={() => openEditSalaryModal(sal)}
                      class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-xs font-medium rounded-md transition-all"
                    >
                      Edit Tier
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Modal: Batch Payroll Generation -->
{#if showBatchModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white dark:bg-slate-800 rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 dark:border-slate-700">
      <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
        <span>⚡</span> Run Monthly Payroll Batch
      </h3>
      <p class="text-xs text-slate-500 mt-1">
        This will compute and generate pending payroll records for all active staff who have configured salary tiers. Existing records will be safely preserved.
      </p>

      <div class="mt-4 space-y-3">
        <div>
          <label for="batch-month-select" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Target Month</label>
          <select
            id="batch-month-select"
            bind:value={batchForm.payroll_month}
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
          >
            {#each months as m}
              <option value={m.value}>{m.name}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="batch-year-select" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Target Year</label>
          <select
            id="batch-year-select"
            bind:value={batchForm.payroll_year}
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
          >
            {#each years as y}
              <option value={y}>{y}</option>
            {/each}
          </select>
        </div>
      </div>

      <div class="mt-6 flex justify-end gap-3">
        <button
          type="button"
          on:click={() => (showBatchModal = false)}
          class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
        >
          Cancel
        </button>
        <button
          type="button"
          on:click={runBatchGeneration}
          disabled={isSubmitting}
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm disabled:opacity-50"
        >
          {isSubmitting ? 'Generating...' : 'Confirm & Run'}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Modal: Salary Tier Configuration -->
{#if showSalaryModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white dark:bg-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 dark:border-slate-700">
      <h3 class="text-lg font-bold text-slate-900 dark:text-white">
        {editingSalary ? 'Edit Salary Structure' : 'Configure Staff Salary Tier'}
      </h3>
      <div class="mt-4 space-y-3">
        {#if !editingSalary}
          <div>
            <label for="salary-staff-select" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Select Staff Member</label>
            <select
              id="salary-staff-select"
              bind:value={salaryForm.staff}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            >
              {#each staffList as st}
                <option value={st.id}>{st.first_name} {st.last_name} (@{st.username})</option>
              {/each}
            </select>
          </div>
        {/if}

        <div>
          <label for="salary-designation-input" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Designation / Faculty Rank</label>
          <input
            id="salary-designation-input"
            type="text"
            bind:value={salaryForm.designation}
            placeholder="e.g. Associate Professor, Lecturer, Lab Assistant"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="salary-base-input" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Base Monthly Salary ($)</label>
            <input
              id="salary-base-input"
              type="number"
              step="0.01"
              bind:value={salaryForm.base_salary}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            />
          </div>
          <div>
            <label for="salary-allowance-input" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Monthly Allowance ($)</label>
            <input
              id="salary-allowance-input"
              type="number"
              step="0.01"
              bind:value={salaryForm.allowance}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="salary-tax-input" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Tax Withholding (%)</label>
            <input
              id="salary-tax-input"
              type="number"
              step="0.01"
              bind:value={salaryForm.tax_percentage}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            />
          </div>
          <div>
            <label for="salary-date-input" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Effective Date</label>
            <input
              id="salary-date-input"
              type="date"
              bind:value={salaryForm.effective_date}
              class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
            />
          </div>
        </div>

        <div class="flex items-center gap-2 pt-2">
          <input
            id="salary_is_active"
            type="checkbox"
            bind:checked={salaryForm.is_active}
            class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label for="salary_is_active" class="text-sm font-medium text-slate-700 dark:text-slate-300">
            Active salary profile eligible for automatic payroll runs
          </label>
        </div>
      </div>

      <div class="mt-6 flex justify-end gap-3">
        <button
          type="button"
          on:click={() => (showSalaryModal = false)}
          class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
        >
          Cancel
        </button>
        <button
          type="button"
          on:click={saveSalaryStructure}
          disabled={isSubmitting}
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm disabled:opacity-50"
        >
          {isSubmitting ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Modal: Mark Payroll as Paid / Disbursed -->
{#if showMarkPaidModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white dark:bg-slate-800 rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 dark:border-slate-700">
      <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
        <span>💵</span> Disburse Salary Payment
      </h3>
      <p class="text-xs text-slate-500 mt-1">
        Confirm disbursement of <b>${parseFloat(targetPayroll?.net_salary || 0).toFixed(2)}</b> to <b>{targetPayroll?.staff_name}</b>.
      </p>

      <div class="mt-4 space-y-3">
        <div>
          <label for="payment-method-select" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Payment Method</label>
          <select
            id="payment-method-select"
            bind:value={markPaidForm.payment_method}
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
          >
            <option value="Bank Transfer">Bank Transfer (Direct Deposit)</option>
            <option value="Cheque">Company Cheque</option>
            <option value="Cash">Cash Voucher</option>
          </select>
        </div>

        <div>
          <label for="payment-date-input" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Disbursement Date</label>
          <input
            id="payment-date-input"
            type="date"
            bind:value={markPaidForm.payment_date}
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
          />
        </div>

        <div>
          <label for="payment-remarks-input" class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Transaction Ref / Remarks</label>
          <input
            id="payment-remarks-input"
            type="text"
            bind:value={markPaidForm.remarks}
            placeholder="e.g. Bank Wire Ref #TXN99824"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-200"
          />
        </div>
      </div>

      <div class="mt-6 flex justify-end gap-3">
        <button
          type="button"
          on:click={() => (showMarkPaidModal = false)}
          class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
        >
          Cancel
        </button>
        <button
          type="button"
          on:click={submitMarkPaid}
          disabled={isSubmitting}
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold rounded-lg shadow-sm disabled:opacity-50"
        >
          {isSubmitting ? 'Processing...' : 'Confirm Paid'}
        </button>
      </div>
    </div>
  </div>
{/if}
