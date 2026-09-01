<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Bell, Trash2, CheckCircle2, Megaphone } from 'lucide-svelte';

  let notifications = $state([]);
  let loading = $state(true);
  let errorMsg = $state('');

  async function loadNotifications() {
    loading = true;
    try {
      notifications = await api.getStudentNotifications();
    } catch (err) {
      errorMsg = err.message || 'Failed to load notifications';
    } finally {
      loading = false;
    }
  }

  async function deleteNotif(id) {
    try {
      await api.deleteStudentNotification(id);
      notifications = notifications.filter(n => n.id !== id);
    } catch (err) {
      alert(err.message || 'Failed to delete notification');
    }
  }

  onMount(() => {
    loadNotifications();
  });
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <Bell class="text-blue-600" size={26} />
        My Campus Notifications
      </h1>
      <p class="text-sm text-slate-500 mt-1">Official announcements and updates from campus administration</p>
    </div>
    <span class="bg-blue-50 text-blue-700 text-xs font-semibold px-3 py-1 rounded-full border border-blue-100">
      {notifications.length} Total
    </span>
  </div>

  <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
    {#if loading}
      <div class="p-12 text-center text-slate-400">Loading your notifications...</div>
    {:else if notifications.length === 0}
      <div class="py-16 text-center text-slate-400 space-y-2">
        <CheckCircle2 size={36} class="mx-auto text-slate-300" />
        <p class="text-base font-medium text-slate-600">All caught up!</p>
        <p class="text-xs text-slate-400">You have no pending announcements or alerts.</p>
      </div>
    {:else}
      <div class="divide-y divide-slate-100">
        {#each notifications as item}
          <div class="py-4.5 first:pt-0 last:pb-0 flex items-start justify-between gap-4 group">
            <div class="flex items-start gap-3.5">
              <div class="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Megaphone size={18} />
              </div>
              <div class="space-y-1">
                <p class="text-sm text-slate-800 font-medium leading-relaxed">{item.message}</p>
                <div class="flex items-center gap-3 text-xs text-slate-400">
                  <span>{new Date(item.created_at).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}</span>
                  <span>&bull;</span>
                  <span>{new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </div>
            </div>

            <button
              class="text-slate-300 hover:text-red-600 p-1.5 rounded-lg hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
              onclick={() => deleteNotif(item.id)}
              title="Delete announcement"
            >
              <Trash2 size={16} />
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>
