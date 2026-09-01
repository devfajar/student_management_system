<script>
  import { onMount } from 'svelte';
  import { auth } from '../authStore.svelte.js';
  import { api } from '../api.js';
  import { LogOut, User, Menu, Bell, X, CheckCircle2, Megaphone } from 'lucide-svelte';

  let { currentView = $bindable(), toggleSidebar } = $props();

  let showNotifications = $state(false);
  let notifications = $state([]);
  let loadingNotifications = $state(false);

  function getRoleName(type) {
    if (type === '1') return 'Admin (HOD)';
    if (type === '2') return 'Staff';
    if (type === '3') return 'Student';
    return 'User';
  }

  async function fetchNotifications() {
    if (!auth.isAuthenticated || !auth.user) return;
    const uType = String(auth.user.user_type);
    try {
      loadingNotifications = true;
      if (uType === '3') {
        notifications = await api.getStudentNotifications();
      } else if (uType === '2') {
        notifications = await api.getStaffNotifications();
      } else if (uType === '1') {
        const hist = await api.getAdminNotificationHistory();
        notifications = [
          ...(hist.student_notifications || []).map(n => ({ ...n, type: 'Student Broadcast' })),
          ...(hist.staff_notifications || []).map(n => ({ ...n, type: 'Staff Broadcast' }))
        ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 8);
      }
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      loadingNotifications = false;
    }
  }

  async function removeNotification(id, e) {
    e?.stopPropagation();
    const uType = String(auth.user?.user_type);
    try {
      if (uType === '3') {
        await api.deleteStudentNotification(id);
      } else if (uType === '2') {
        await api.deleteStaffNotification(id);
      }
      notifications = notifications.filter(n => n.id !== id);
    } catch (err) {
      console.error('Failed to remove notification:', err);
    }
  }

  onMount(() => {
    fetchNotifications();
  });
</script>

<header class="h-16 bg-white border-b border-slate-200 flex justify-between items-center px-6 shadow-sm z-20 relative">
  <div class="flex items-center gap-3">
    {#if toggleSidebar}
      <button class="text-slate-700 hover:text-blue-600 transition-colors p-1" onclick={toggleSidebar} aria-label="Toggle sidebar">
        <Menu size={20} />
      </button>
    {/if}
    <div class="flex items-center gap-2.5">
      <h3 class="text-base font-semibold text-slate-800 tracking-tight">Student Management System</h3>
      <span class="bg-blue-50 text-blue-600 border border-blue-200 text-xs font-semibold px-2.5 py-0.5 rounded-full">
        {getRoleName(auth.user?.user_type)}
      </span>
    </div>
  </div>

  <div class="flex items-center gap-3">
    <!-- Notification Bell -->
    <div class="relative">
      <button
        class="relative p-2 text-slate-600 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-colors"
        onclick={() => { showNotifications = !showNotifications; if (showNotifications) fetchNotifications(); }}
        aria-label="Notifications"
      >
        <Bell size={19} />
        {#if notifications.length > 0}
          <span class="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
            {notifications.length > 9 ? '9+' : notifications.length}
          </span>
        {/if}
      </button>

      {#if showNotifications}
        <div class="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-xl border border-slate-200 py-3 z-50 animate-in fade-in zoom-in-95 duration-150">
          <div class="flex items-center justify-between px-4 pb-2 border-b border-slate-100">
            <div class="flex items-center gap-2">
              <Megaphone size={16} class="text-blue-600" />
              <h4 class="text-sm font-semibold text-slate-800">Announcements & Alerts</h4>
            </div>
            <span class="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">{notifications.length} recent</span>
          </div>

          <div class="max-h-72 overflow-y-auto divide-y divide-slate-100">
            {#if loadingNotifications}
              <div class="p-4 text-center text-sm text-slate-400">Loading announcements...</div>
            {:else if notifications.length === 0}
              <div class="p-6 text-center text-slate-400">
                <CheckCircle2 size={24} class="mx-auto text-slate-300 mb-2" />
                <p class="text-xs">No new notifications</p>
              </div>
            {:else}
              {#each notifications as notif}
                <div class="p-3 hover:bg-slate-50 transition-colors flex items-start justify-between gap-2 group">
                  <div class="flex-1">
                    {#if notif.type}
                      <span class="text-[10px] font-semibold uppercase tracking-wider text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
                        {notif.type}
                      </span>
                    {/if}
                    <p class="text-xs text-slate-700 mt-1 leading-relaxed">{notif.message}</p>
                    <span class="text-[10px] text-slate-400 mt-1 block">
                      {new Date(notif.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                    </span>
                  </div>
                  {#if String(auth.user?.user_type) !== '1'}
                    <button
                      class="text-slate-300 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      onclick={(e) => removeNotification(notif.id, e)}
                      title="Dismiss notification"
                    >
                      <X size={14} />
                    </button>
                  {/if}
                </div>
              {/each}
            {/if}
          </div>

          {#if String(auth.user?.user_type) === '1'}
            <div class="px-4 pt-2 border-t border-slate-100 mt-1 text-center">
              <button
                class="text-xs font-semibold text-blue-600 hover:text-blue-700"
                onclick={() => { currentView = 'broadcast-notifications'; showNotifications = false; }}
              >
                Send New Broadcast &rarr;
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- User Profile Button -->
    <button
      class="flex items-center gap-2 p-1.5 hover:bg-slate-100 rounded-lg transition-colors text-left"
      onclick={() => currentView = 'profile'}
    >
      <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-semibold text-xs">
        <User size={15} />
      </div>
      <div class="hidden sm:block">
        <span class="text-xs font-medium text-slate-700 block leading-tight">
          {auth.user?.first_name ? `${auth.user.first_name} ${auth.user.last_name}` : auth.user?.username}
        </span>
      </div>
    </button>

    <!-- Logout Button -->
    <button
      class="flex items-center gap-1.5 px-3 py-1.5 border border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 rounded-lg text-xs font-medium transition-all"
      onclick={() => auth.logout()}
    >
      <LogOut size={14} />
      <span class="hidden sm:inline">Logout</span>
    </button>
  </div>
</header>

