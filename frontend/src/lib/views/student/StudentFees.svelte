<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import Modal from '../../components/Modal.svelte';
  import {
    CircleDollarSign, Receipt, CreditCard, Calendar,
    CheckCircle2, AlertCircle, Printer, ArrowUpRight
  } from 'lucide-svelte';

  let loading = $state(true);
  let errorMsg = $state('');
  let invoices = $state([]);
  let summary = $state({
    total_billed: 0,
    total_paid: 0,
    total_balance: 0,
    unpaid_invoices_count: 0
  });

  // Receipt Modal
  let showReceiptModal = $state(false);
  let receiptData = $state(null);

  async function loadStudentInvoices() {
    loading = true;
    try {
      const data = await api.getMyFeeInvoices();
      invoices = data.invoices || [];
      summary = data.summary || {
        total_billed: 0,
        total_paid: 0,
        total_balance: 0,
        unpaid_invoices_count: 0
      };
    } catch (err) {
      errorMsg = err.message || 'Failed to load fee statement';
    } finally {
      loading = false;
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

  onMount(() => {
    loadStudentInvoices();
  });
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
      <CircleDollarSign class="text-blue-600" size={28} />
      My Fee Invoices & Financial Statement
    </h1>
    <p class="text-sm text-slate-500 mt-1">Review your tuition dues, payment receipts, and balance ledger</p>
  </div>

  {#if errorMsg}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-2 text-sm shadow-sm">
      <AlertCircle size={18} />
      <span>{errorMsg}</span>
    </div>
  {/if}

  <!-- Financial Summary Cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-1">
      <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Billed</span>
      <p class="text-2xl font-black text-slate-800">${Number(summary.total_billed).toFixed(2)}</p>
      <span class="text-xs text-slate-400">Institutional tuition fees</span>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-1">
      <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Paid</span>
      <p class="text-2xl font-black text-emerald-600">${Number(summary.total_paid).toFixed(2)}</p>
      <span class="text-xs text-emerald-600 font-medium">Cleared payments</span>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-1">
      <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Outstanding Balance</span>
      <p class="text-2xl font-black text-red-600">${Number(summary.total_balance).toFixed(2)}</p>
      <span class="text-xs text-red-500 font-medium">{summary.unpaid_invoices_count} pending invoice(s)</span>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-1">
      <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Payment Status</span>
      <div class="pt-1">
        {#if summary.total_balance === 0 && summary.total_billed > 0}
          <span class="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold px-3 py-1 rounded-full">All Fees Cleared</span>
        {:else if summary.total_paid > 0}
          <span class="bg-amber-50 text-amber-700 border border-amber-200 text-xs font-bold px-3 py-1 rounded-full">Partial Dues</span>
        {:else if summary.total_billed === 0}
          <span class="bg-slate-100 text-slate-600 text-xs font-bold px-3 py-1 rounded-full">No Invoices</span>
        {:else}
          <span class="bg-red-50 text-red-700 border border-red-200 text-xs font-bold px-3 py-1 rounded-full">Pending Payment</span>
        {/if}
      </div>
      <span class="text-xs text-slate-400">Current financial standing</span>
    </div>
  </div>

  <!-- Invoices Table -->
  <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-base font-bold text-slate-800">Fee Invoices Breakdown</h2>
      <span class="text-xs font-medium text-slate-500">{invoices.length} Record(s)</span>
    </div>

    <div class="overflow-x-auto border border-slate-100 rounded-xl">
      <table class="w-full text-left text-sm text-slate-600">
        <thead class="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <tr>
            <th class="px-4 py-3">Invoice #</th>
            <th class="px-4 py-3">Fee Title</th>
            <th class="px-4 py-3">Due Date</th>
            <th class="px-4 py-3">Total Amount</th>
            <th class="px-4 py-3">Amount Paid</th>
            <th class="px-4 py-3">Balance</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3 text-right">Receipt</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          {#if invoices.length === 0}
            <tr>
              <td colspan="8" class="text-center py-8 text-slate-400">No fee invoices issued for your account yet.</td>
            </tr>
          {:else}
            {#each invoices as inv}
              <tr class="hover:bg-slate-50/80 transition-colors">
                <td class="px-4 py-3 text-xs font-mono text-slate-400">#INV-{inv.id}</td>
                <td class="px-4 py-3 font-semibold text-slate-800">{inv.fee_name}</td>
                <td class="px-4 py-3 text-xs text-slate-500">{inv.due_date || 'N/A'}</td>
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
                  {#if inv.payments && inv.payments.length > 0}
                    <button
                      class="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg text-xs font-semibold transition-colors"
                      onclick={() => openReceipt(inv.payments[inv.payments.length - 1].id)}
                    >
                      <Receipt size={13} />
                      <span>View Receipt</span>
                    </button>
                  {:else}
                    <span class="text-xs text-slate-400">No payment</span>
                  {/if}
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- Modal: Printable Receipt -->
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
