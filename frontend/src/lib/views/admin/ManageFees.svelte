<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import {
    CircleDollarSign, Plus, Filter, Search, Receipt,
    CreditCard, Calendar, CheckCircle2, AlertCircle, Trash2,
    Printer, Send, FileText, ArrowRight, FileDown
  } from 'lucide-svelte';

  let activeTab = $state('invoices'); // 'invoices' or 'structures'
  let loading = $state(true);
  let errorMsg = $state('');
  let successMsg = $state('');

  let courses = $state([]);
  let sessions = $state([]);
  let feeStructures = $state([]);
  let invoices = $state([]);

  // Filters
  let filterCourse = $state('');
  let filterStatus = $state('');
  let searchQuery = $state('');

  // Structure Form Modal
  let showStructureModal = $state(false);
  let isEditingStructure = $state(false);
  let editingStructureId = $state(null);
  let structureForm = $state({
    fee_name: '',
    course_id: '',
    session_year_id: '',
    tuition_fee: 0,
    lab_fee: 0,
    library_fee: 0,
    exam_fee: 0,
    other_fee: 0,
    due_date: ''
  });

  // Generate Invoices Modal
  let showGenerateModal = $state(false);
  let generateFeeStructureId = $state('');
  let generating = $state(false);

  // Collect Payment Modal
  let showPaymentModal = $state(false);
  let selectedInvoice = $state(null);
  let paymentForm = $state({
    amount_paid: 0,
    payment_method: 'Cash',
    transaction_id: '',
    remarks: ''
  });
  let collecting = $state(false);

  // Receipt Modal
  let showReceiptModal = $state(false);
  let receiptData = $state(null);

  async function loadInitialData() {
    loading = true;
    try {
      const [coursesData, sessionsData, structData, invData] = await Promise.all([
        api.getCourses(),
        api.getSessions(),
        api.getFeeStructures(),
        api.getFeeInvoices()
      ]);
      courses = coursesData;
      sessions = sessionsData;
      feeStructures = structData;
      invoices = invData;

      if (courses.length > 0) structureForm.course_id = courses[0].id;
      if (sessions.length > 0) structureForm.session_year_id = sessions[0].id;
      if (feeStructures.length > 0) generateFeeStructureId = feeStructures[0].id;
    } catch (err) {
      errorMsg = err.message || 'Failed to load fee records';
    } finally {
      loading = false;
    }
  }

  async function refreshInvoices() {
    try {
      const params = {};
      if (filterCourse) params.course_id = filterCourse;
      if (filterStatus) params.payment_status = filterStatus;
      invoices = await api.getFeeInvoices(params);
    } catch (err) {
      console.error(err);
    }
  }

  async function refreshStructures() {
    try {
      feeStructures = await api.getFeeStructures();
    } catch (err) {
      console.error(err);
    }
  }

  function openCreateStructure() {
    isEditingStructure = false;
    editingStructureId = null;
    structureForm = {
      fee_name: '',
      course_id: courses[0]?.id || '',
      session_year_id: sessions[0]?.id || '',
      tuition_fee: 0,
      lab_fee: 0,
      library_fee: 0,
      exam_fee: 0,
      other_fee: 0,
      due_date: ''
    };
    showStructureModal = true;
  }

  async function saveStructure() {
    try {
      if (isEditingStructure) {
        await api.updateFeeStructure(editingStructureId, structureForm);
        successMsg = 'Fee structure updated successfully';
      } else {
        await api.createFeeStructure(structureForm);
        successMsg = 'Fee structure created successfully';
      }
      showStructureModal = false;
      await refreshStructures();
    } catch (err) {
      alert(err.message || 'Failed to save fee structure');
    }
  }

  async function deleteStructure(id) {
    if (!confirm('Are you sure you want to delete this fee structure template?')) return;
    try {
      await api.deleteFeeStructure(id);
      await refreshStructures();
      successMsg = 'Fee structure deleted';
    } catch (err) {
      alert(err.message || 'Failed to delete');
    }
  }

  async function handleGenerateInvoices() {
    generating = true;
    try {
      const res = await api.generateFeeInvoices({ fee_structure_id: generateFeeStructureId });
      successMsg = res.message || 'Fee invoices generated';
      showGenerateModal = false;
      await refreshInvoices();
    } catch (err) {
      alert(err.message || 'Failed to generate invoices');
    } finally {
      generating = false;
    }
  }

  function openPaymentModal(invoice) {
    selectedInvoice = invoice;
    paymentForm = {
      amount_paid: invoice.balance_amount,
      payment_method: 'Cash',
      transaction_id: '',
      remarks: ''
    };
    showPaymentModal = true;
  }

  async function handleCollectPayment() {
    collecting = true;
    try {
      const res = await api.collectFeePayment({
        invoice_id: selectedInvoice.id,
        ...paymentForm
      });
      successMsg = res.message || 'Payment recorded successfully';
      showPaymentModal = false;
      await refreshInvoices();

      // Open receipt
      if (res.payment?.id) {
        await openReceipt(res.payment.id);
      }
    } catch (err) {
      alert(err.message || 'Failed to collect payment');
    } finally {
      collecting = false;
    }
  }

  async function openReceipt(paymentId) {
    try {
      receiptData = await api.getFeeReceipt(paymentId);
      showReceiptModal = true;
    } catch (err) {
      alert(err.message || 'Failed to load receipt');
    }
  }

  const filteredInvoices = $derived(
    invoices.filter(inv => {
      const matchesSearch = !searchQuery ||
        inv.student_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inv.student_username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inv.fee_name?.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSearch;
    })
  );

  onMount(() => {
    loadInitialData();
  });
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <CircleDollarSign class="text-blue-600" size={28} />
        Student Fee & Payment Management
      </h1>
      <p class="text-sm text-slate-500 mt-1">Configure institutional fee structures, generate student invoices, and collect tuition dues</p>
    </div>

    <!-- Tab Switcher -->
    <div class="flex items-center bg-slate-200/80 p-1 rounded-xl">
      <button
        class="px-4 py-2 rounded-lg text-xs font-semibold transition-all {activeTab === 'invoices' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'}"
        onclick={() => activeTab = 'invoices'}
      >
        Student Invoices ({invoices.length})
      </button>
      <button
        class="px-4 py-2 rounded-lg text-xs font-semibold transition-all {activeTab === 'structures' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'}"
        onclick={() => activeTab = 'structures'}
      >
        Fee Structures ({feeStructures.length})
      </button>
    </div>
  </div>

  {#if successMsg}
    <div class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl flex items-center justify-between text-sm shadow-sm">
      <div class="flex items-center gap-2">
        <CheckCircle2 size={18} />
        <span>{successMsg}</span>
      </div>
      <button class="text-emerald-500 hover:text-emerald-800 font-bold" onclick={() => successMsg = ''}>&times;</button>
    </div>
  {/if}

  {#if activeTab === 'invoices'}
    <!-- Tab 1: Student Fee Invoices & Ledger -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
      <!-- Toolbar -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Search -->
        <div class="relative flex-1 max-w-sm">
          <Search size={16} class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by student name or fee..."
            bind:value={searchQuery}
            class="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        <!-- Filters & Generate Button -->
        <div class="flex flex-wrap items-center gap-3">
          <select
            bind:value={filterCourse}
            onchange={refreshInvoices}
            class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:outline-none"
          >
            <option value="">All Courses</option>
            {#each courses as c}
              <option value={c.id}>{c.course_name}</option>
            {/each}
          </select>

          <select
            bind:value={filterStatus}
            onchange={refreshInvoices}
            class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="Paid">Paid</option>
            <option value="Partial">Partial</option>
            <option value="Unpaid">Unpaid</option>
          </select>

          <button
            class="flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-xs font-semibold shadow-sm transition-all"
            onclick={() => api.exportFeesCsv({ course_id: filterCourse, status: filterStatus })}
          >
            <FileDown size={14} class="text-blue-600" />
            <span>Export CSV</span>
          </button>

          <button
            class="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all"
            onclick={() => showGenerateModal = true}
          >
            <Plus size={14} />
            <span>Generate Invoices</span>
          </button>
        </div>
      </div>

      <!-- Invoices Table -->
      <div class="overflow-x-auto border border-slate-100 rounded-xl">
        <table class="w-full text-left text-sm text-slate-600">
          <thead class="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <tr>
              <th class="px-4 py-3">Invoice ID</th>
              <th class="px-4 py-3">Student Name</th>
              <th class="px-4 py-3">Course</th>
              <th class="px-4 py-3">Fee Title</th>
              <th class="px-4 py-3">Total Amount</th>
              <th class="px-4 py-3">Paid</th>
              <th class="px-4 py-3">Balance</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            {#if filteredInvoices.length === 0}
              <tr>
                <td colspan="9" class="text-center py-8 text-slate-400">No fee invoices found matching criteria.</td>
              </tr>
            {:else}
              {#each filteredInvoices as inv}
                <tr class="hover:bg-slate-50/80 transition-colors">
                  <td class="px-4 py-3 text-xs font-mono text-slate-400">#INV-{inv.id}</td>
                  <td class="px-4 py-3 font-semibold text-slate-800">{inv.student_name} <span class="text-xs font-normal text-slate-400">(@{inv.student_username})</span></td>
                  <td class="px-4 py-3 text-xs"><span class="bg-slate-100 px-2 py-0.5 rounded text-slate-700">{inv.course_name}</span></td>
                  <td class="px-4 py-3 font-medium text-slate-700">{inv.fee_name}</td>
                  <td class="px-4 py-3 font-semibold text-slate-800">${Number(inv.total_amount).toFixed(2)}</td>
                  <td class="px-4 py-3 font-medium text-emerald-600">${Number(inv.paid_amount).toFixed(2)}</td>
                  <td class="px-4 py-3 font-medium text-red-600">${Number(inv.balance_amount).toFixed(2)}</td>
                  <td class="px-4 py-3">
                    {#if inv.payment_status === 'Paid'}
                      <span class="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold px-2 py-0.5 rounded-full">Paid</span>
                    {:else if inv.payment_status === 'Partial'}
                      <span class="bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold px-2 py-0.5 rounded-full">Partial</span>
                    {:else}
                      <span class="bg-red-50 text-red-700 border border-red-200 text-xs font-semibold px-2 py-0.5 rounded-full">Unpaid</span>
                    {/if}
                  </td>
                  <td class="px-4 py-3 text-right">
                    <div class="flex items-center justify-end gap-2">
                      {#if inv.payment_status !== 'Paid'}
                        <button
                          class="flex items-center gap-1 px-2.5 py-1 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg text-xs font-semibold transition-colors"
                          onclick={() => openPaymentModal(inv)}
                        >
                          <CreditCard size={13} />
                          <span>Collect</span>
                        </button>
                      {/if}
                      {#if inv.payments && inv.payments.length > 0}
                        <button
                          class="flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg text-xs font-medium transition-colors"
                          onclick={() => openReceipt(inv.payments[inv.payments.length - 1].id)}
                          title="View Receipt"
                        >
                          <Receipt size={13} />
                          <span>Receipt</span>
                        </button>
                      {/if}
                    </div>
                  </td>
                </tr>
              {/each}
            {/if}
          </tbody>
        </table>
      </div>
    </div>

  {:else}
    <!-- Tab 2: Fee Structure Templates -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-800">Fee Structure Templates</h2>
          <p class="text-xs text-slate-500">Define course tuition fees and break-up items</p>
        </div>
        <button
          class="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all"
          onclick={openCreateStructure}
        >
          <Plus size={15} />
          <span>New Structure</span>
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {#if feeStructures.length === 0}
          <div class="col-span-full py-12 text-center text-slate-400">
            No fee structure templates defined yet. Click "New Structure" to create one.
          </div>
        {:else}
          {#each feeStructures as fs}
            <div class="border border-slate-200 rounded-2xl p-5 hover:border-slate-300 transition-all space-y-4 bg-slate-50/50">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="font-bold text-slate-800 text-base">{fs.fee_name}</h3>
                  <p class="text-xs text-slate-500">{fs.course_name} &bull; {fs.session_year}</p>
                </div>
                <button
                  class="text-slate-400 hover:text-red-600 p-1"
                  onclick={() => deleteStructure(fs.id)}
                  title="Delete structure"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <!-- Fee Breakdown List -->
              <div class="space-y-1.5 text-xs text-slate-600 divide-y divide-slate-100">
                <div class="flex justify-between pt-1"><span>Tuition:</span><span class="font-semibold">${Number(fs.tuition_fee).toFixed(2)}</span></div>
                <div class="flex justify-between pt-1"><span>Laboratory:</span><span class="font-semibold">${Number(fs.lab_fee).toFixed(2)}</span></div>
                <div class="flex justify-between pt-1"><span>Library:</span><span class="font-semibold">${Number(fs.library_fee).toFixed(2)}</span></div>
                <div class="flex justify-between pt-1"><span>Examination:</span><span class="font-semibold">${Number(fs.exam_fee).toFixed(2)}</span></div>
                <div class="flex justify-between pt-1"><span>Other / Misc:</span><span class="font-semibold">${Number(fs.other_fee).toFixed(2)}</span></div>
              </div>

              <div class="pt-2 border-t border-slate-200 flex justify-between items-center">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Total Fee</span>
                <span class="text-lg font-bold text-blue-600">${Number(fs.total_amount).toFixed(2)}</span>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  {/if}
</div>

<!-- Modal 1: Create / Edit Fee Structure -->
<Modal show={showStructureModal} title="Configure Fee Structure Template" onclose={() => showStructureModal = false}>
  <form onsubmit={(e) => { e.preventDefault(); saveStructure(); }} class="space-y-4">
    <div>
      <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Fee Title</label>
      <input type="text" required bind:value={structureForm.fee_name} placeholder="e.g. Semester 1 Tuition 2026" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Target Course</label>
        <select bind:value={structureForm.course_id} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm">
          {#each courses as c}
            <option value={c.id}>{c.course_name}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Session Year</label>
        <select bind:value={structureForm.session_year_id} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm">
          {#each sessions as s}
            <option value={s.id}>{s.session_start_year} TO {s.session_end_year}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Tuition Fee ($)</label>
        <input type="number" step="0.01" bind:value={structureForm.tuition_fee} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Lab Fee ($)</label>
        <input type="number" step="0.01" bind:value={structureForm.lab_fee} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
      </div>
    </div>

    <div class="grid grid-cols-3 gap-3">
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Library ($)</label>
        <input type="number" step="0.01" bind:value={structureForm.library_fee} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Exam ($)</label>
        <input type="number" step="0.01" bind:value={structureForm.exam_fee} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
      </div>
      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Other ($)</label>
        <input type="number" step="0.01" bind:value={structureForm.other_fee} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
      </div>
    </div>

    <div>
      <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Payment Due Date</label>
      <input type="date" bind:value={structureForm.due_date} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
    </div>

    <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
      <button type="button" class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-xl" onclick={() => showStructureModal = false}>Cancel</button>
      <button type="submit" class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm">Save Structure</button>
    </div>
  </form>
</Modal>

<!-- Modal 2: Generate Invoices -->
<Modal show={showGenerateModal} title="Issue Invoices to Students" onclose={() => showGenerateModal = false}>
  <form onsubmit={(e) => { e.preventDefault(); handleGenerateInvoices(); }} class="space-y-4">
    <p class="text-xs text-slate-500">Select a fee structure template. Invoices will automatically be generated for all enrolled students who do not yet have one.</p>

    <div>
      <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Select Fee Template</label>
      <select bind:value={generateFeeStructureId} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm">
        {#each feeStructures as fs}
          <option value={fs.id}>{fs.fee_name} (${Number(fs.total_amount).toFixed(2)}) - {fs.course_name}</option>
        {/each}
      </select>
    </div>

    <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
      <button type="button" class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-xl" onclick={() => showGenerateModal = false}>Cancel</button>
      <button type="submit" disabled={generating} class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm">
        {generating ? 'Generating...' : 'Issue Invoices'}
      </button>
    </div>
  </form>
</Modal>

<!-- Modal 3: Collect Payment -->
{#if selectedInvoice}
  <Modal show={showPaymentModal} title="Collect Student Fee Payment" onclose={() => showPaymentModal = false}>
    <form onsubmit={(e) => { e.preventDefault(); handleCollectPayment(); }} class="space-y-4">
      <div class="bg-blue-50/60 p-4 rounded-xl space-y-1 text-xs">
        <p><span class="font-semibold text-slate-700">Student:</span> {selectedInvoice.student_name} (@{selectedInvoice.student_username})</p>
        <p><span class="font-semibold text-slate-700">Fee Title:</span> {selectedInvoice.fee_name}</p>
        <div class="flex justify-between font-bold text-sm text-blue-900 pt-2 border-t border-blue-100">
          <span>Remaining Balance:</span>
          <span>${Number(selectedInvoice.balance_amount).toFixed(2)}</span>
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Amount to Pay ($)</label>
        <input
          type="number"
          step="0.01"
          max={selectedInvoice.balance_amount}
          required
          bind:value={paymentForm.amount_paid}
          class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm font-bold text-slate-800"
        />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Payment Method</label>
          <select bind:value={paymentForm.payment_method} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm">
            <option value="Cash">Cash</option>
            <option value="Bank Transfer">Bank Transfer</option>
            <option value="Card">Card</option>
            <option value="Online">Online</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Transaction Ref #</label>
          <input type="text" placeholder="Optional" bind:value={paymentForm.transaction_id} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Remarks / Note</label>
        <input type="text" placeholder="e.g. Receipt #123" bind:value={paymentForm.remarks} class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm" />
      </div>

      <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
        <button type="button" class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-xl" onclick={() => showPaymentModal = false}>Cancel</button>
        <button type="submit" disabled={collecting} class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-semibold shadow-sm">
          {collecting ? 'Processing...' : 'Record Payment & Issue Receipt'}
        </button>
      </div>
    </form>
  </Modal>
{/if}

<!-- Modal 4: Printable Receipt -->
{#if receiptData}
  <Modal show={showReceiptModal} title="Official Fee Payment Receipt" onclose={() => showReceiptModal = false}>
    <div class="p-4 space-y-5 print:p-0">
      <!-- Receipt Header -->
      <div class="text-center border-b border-slate-200 pb-4">
        <h2 class="text-lg font-bold text-slate-800">Student Management System</h2>
        <p class="text-xs text-slate-500">Official Campus Bursar / Payment Receipt</p>
        <span class="inline-block mt-2 font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200">
          {receiptData.receipt_no}
        </span>
      </div>

      <!-- Payer & Fee Details -->
      <div class="grid grid-cols-2 gap-4 text-xs">
        <div>
          <p class="text-slate-400 uppercase font-semibold">Student Information</p>
          <p class="font-bold text-slate-800 text-sm">{receiptData.student?.name}</p>
          <p class="text-slate-600">ID: #{receiptData.student?.id} &bull; {receiptData.student?.username}</p>
          <p class="text-slate-600">{receiptData.student?.course}</p>
        </div>
        <div class="text-right">
          <p class="text-slate-400 uppercase font-semibold">Payment Details</p>
          <p class="font-semibold text-slate-800">{new Date(receiptData.payment_date).toLocaleDateString([], { dateStyle: 'long' })}</p>
          <p class="text-slate-600">Method: {receiptData.payment_method}</p>
          {#if receiptData.transaction_id}
            <p class="text-slate-600">Ref: {receiptData.transaction_id}</p>
          {/if}
        </div>
      </div>

      <!-- Financial Ledger Summary -->
      <div class="border border-slate-200 rounded-xl overflow-hidden text-xs">
        <table class="w-full text-left">
          <thead class="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
            <tr>
              <th class="p-2.5">Description</th>
              <th class="p-2.5 text-right">Amount</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr>
              <td class="p-2.5 font-medium">{receiptData.fee?.fee_name} (Total Billed)</td>
              <td class="p-2.5 text-right">${Number(receiptData.fee?.total_amount).toFixed(2)}</td>
            </tr>
            <tr class="bg-emerald-50/50 font-bold text-emerald-800">
              <td class="p-2.5">Payment Received Today</td>
              <td class="p-2.5 text-right">${Number(receiptData.amount_paid).toFixed(2)}</td>
            </tr>
            <tr class="font-semibold text-slate-700">
              <td class="p-2.5">Total Paid to Date</td>
              <td class="p-2.5 text-right">${Number(receiptData.fee?.total_paid_to_date).toFixed(2)}</td>
            </tr>
            <tr class="bg-slate-50 font-bold text-slate-900">
              <td class="p-2.5">Remaining Balance</td>
              <td class="p-2.5 text-right text-red-600">${Number(receiptData.fee?.remaining_balance).toFixed(2)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
        <button class="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-semibold" onclick={() => window.print()}>
          <Printer size={15} />
          <span>Print Receipt</span>
        </button>
      </div>
    </div>
  </Modal>
{/if}
