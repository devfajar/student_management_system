<script>
  import { onMount } from 'svelte';
  import { api } from '../../api.js';
  import { Megaphone, Send, Users, GraduationCap, Briefcase, Trash2, History, AlertCircle, CheckCircle2 } from 'lucide-svelte';

  let courses = $state([]);
  let targetType = $state('all_students'); // 'all_students', 'course_students', 'all_staff'
  let selectedCourseId = $state('');
  let message = $state('');
  let loading = $state(false);
  let sending = $state(false);
  let successMsg = $state('');
  let errorMsg = $state('');

  let historyStudent = $state([]);
  let historyStaff = $state([]);
  let activeTab = $state('students'); // 'students' or 'staff'

  async function loadData() {
    loading = true;
    try {
      courses = await api.getCourses();
      if (courses.length > 0) {
        selectedCourseId = courses[0].id;
      }
      await loadHistory();
    } catch (err) {
      errorMsg = err.message || 'Failed to load broadcast settings';
    } finally {
      loading = false;
    }
  }

  async function loadHistory() {
    try {
      const res = await api.getAdminNotificationHistory();
      historyStudent = res.student_notifications || [];
      historyStaff = res.staff_notifications || [];
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }

  async function handleSendBroadcast() {
    if (!message.trim()) {
      errorMsg = 'Please type a broadcast message';
      return;
    }

    sending = true;
    errorMsg = '';
    successMsg = '';

    try {
      if (targetType === 'all_students') {
        const res = await api.broadcastToStudents({ message, target_type: 'all' });
        successMsg = res.message || 'Broadcast delivered to all students';
      } else if (targetType === 'course_students') {
        const res = await api.broadcastToStudents({ message, target_type: 'course', course_id: selectedCourseId });
        successMsg = res.message || 'Broadcast delivered to course students';
      } else if (targetType === 'all_staff') {
        const res = await api.broadcastToStaff({ message });
        successMsg = res.message || 'Broadcast delivered to all staff';
      }
      message = '';
      await loadHistory();
    } catch (err) {
      errorMsg = err.message || 'Failed to send broadcast announcement';
    } finally {
      sending = false;
    }
  }

  async function handleDeleteNotification(type, id) {
    if (!confirm('Are you sure you want to delete this notification record?')) return;
    try {
      if (type === 'student') {
        await api.deleteStudentNotification(id);
        historyStudent = historyStudent.filter(n => n.id !== id);
      } else {
        await api.deleteStaffNotification(id);
        historyStaff = historyStaff.filter(n => n.id !== id);
      }
    } catch (err) {
      alert(err.message || 'Failed to delete notification');
    }
  }

  onMount(() => {
    loadData();
  });
</script>

<div class="space-y-6 animate-in fade-in duration-200">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
        <Megaphone class="text-blue-600" size={28} />
        Campus Announcements & Broadcasts
      </h1>
      <p class="text-sm text-slate-500 mt-1">Publish real-time announcements to students and faculty across the institution</p>
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

  {#if errorMsg}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center justify-between text-sm shadow-sm">
      <div class="flex items-center gap-2">
        <AlertCircle size={18} />
        <span>{errorMsg}</span>
      </div>
      <button class="text-red-500 hover:text-red-800 font-bold" onclick={() => errorMsg = ''}>&times;</button>
    </div>
  {/if}

  <!-- Broadcast Composer Card -->
  <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
    <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
      <Send size={18} class="text-blue-600" />
      Create New Broadcast
    </h2>

    <form onsubmit={(e) => { e.preventDefault(); handleSendBroadcast(); }} class="space-y-5">
      <!-- Audience Selection Pills -->
      <div>
        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-2">Select Target Audience</label>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            type="button"
            class="flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all {targetType === 'all_students' ? 'border-blue-600 bg-blue-50/60 ring-2 ring-blue-500/20 text-blue-900' : 'border-slate-200 hover:border-slate-300 text-slate-700'}"
            onclick={() => targetType = 'all_students'}
          >
            <div class="p-2 rounded-lg {targetType === 'all_students' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}">
              <Users size={18} />
            </div>
            <div>
              <p class="text-sm font-semibold">All Students</p>
              <p class="text-xs text-slate-500">Every enrolled student</p>
            </div>
          </button>

          <button
            type="button"
            class="flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all {targetType === 'course_students' ? 'border-blue-600 bg-blue-50/60 ring-2 ring-blue-500/20 text-blue-900' : 'border-slate-200 hover:border-slate-300 text-slate-700'}"
            onclick={() => targetType = 'course_students'}
          >
            <div class="p-2 rounded-lg {targetType === 'course_students' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}">
              <GraduationCap size={18} />
            </div>
            <div>
              <p class="text-sm font-semibold">By Course</p>
              <p class="text-xs text-slate-500">Students in specific major</p>
            </div>
          </button>

          <button
            type="button"
            class="flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all {targetType === 'all_staff' ? 'border-blue-600 bg-blue-50/60 ring-2 ring-blue-500/20 text-blue-900' : 'border-slate-200 hover:border-slate-300 text-slate-700'}"
            onclick={() => targetType = 'all_staff'}
          >
            <div class="p-2 rounded-lg {targetType === 'all_staff' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}">
              <Briefcase size={18} />
            </div>
            <div>
              <p class="text-sm font-semibold">All Faculty / Staff</p>
              <p class="text-xs text-slate-500">Teachers & instructors</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Specific Course Dropdown if targetType === 'course_students' -->
      {#if targetType === 'course_students'}
        <div class="animate-in fade-in slide-in-from-top-2 duration-150">
          <label for="course-select" class="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">Target Course</label>
          <select
            id="course-select"
            bind:value={selectedCourseId}
            class="w-full sm:w-80 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            {#each courses as c}
              <option value={c.id}>{c.course_name}</option>
            {/each}
          </select>
        </div>
      {/if}

      <!-- Message Area -->
      <div>
        <div class="flex justify-between items-center mb-1.5">
          <label for="message-input" class="block text-xs font-semibold uppercase tracking-wider text-slate-600">Announcement Message</label>
          <span class="text-xs text-slate-400">{message.length} characters</span>
        </div>
        <textarea
          id="message-input"
          bind:value={message}
          rows="4"
          placeholder="Type announcement message here (e.g. Schedule changes, exam dates, campus events)..."
          class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none"
        ></textarea>
      </div>

      <!-- Action Button -->
      <div class="flex justify-end">
        <button
          type="submit"
          disabled={sending || !message.trim()}
          class="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-sm hover:shadow transition-all"
        >
          {#if sending}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Broadcasting...</span>
          {:else}
            <Send size={16} />
            <span>Send Broadcast</span>
          {/if}
        </button>
      </div>
    </form>
  </div>

  <!-- Broadcast History Section -->
  <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
        <History size={18} class="text-blue-600" />
        Broadcast History Logs
      </h2>

      <!-- Tab Buttons -->
      <div class="flex items-center bg-slate-100 p-1 rounded-xl">
        <button
          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all {activeTab === 'students' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'}"
          onclick={() => activeTab = 'students'}
        >
          Students ({historyStudent.length})
        </button>
        <button
          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all {activeTab === 'staff' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'}"
          onclick={() => activeTab = 'staff'}
        >
          Staff ({historyStaff.length})
        </button>
      </div>
    </div>

    <!-- Table of logs -->
    <div class="overflow-x-auto border border-slate-100 rounded-xl">
      {#if activeTab === 'students'}
        <table class="w-full text-left text-sm text-slate-600">
          <thead class="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <tr>
              <th class="px-4 py-3">ID</th>
              <th class="px-4 py-3">Recipient Student</th>
              <th class="px-4 py-3">Course</th>
              <th class="px-4 py-3">Message</th>
              <th class="px-4 py-3">Sent At</th>
              <th class="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            {#if historyStudent.length === 0}
              <tr>
                <td colspan="6" class="text-center py-8 text-slate-400">No student announcements sent yet.</td>
              </tr>
            {:else}
              {#each historyStudent as item}
                <tr class="hover:bg-slate-50/80 transition-colors">
                  <td class="px-4 py-3 text-xs font-mono text-slate-400">#{item.id}</td>
                  <td class="px-4 py-3 font-medium text-slate-800">{item.student_name} <span class="text-xs text-slate-400">(@{item.student_username})</span></td>
                  <td class="px-4 py-3 text-xs"><span class="bg-slate-100 px-2 py-0.5 rounded text-slate-700">{item.course_name || 'All Courses'}</span></td>
                  <td class="px-4 py-3 max-w-xs truncate text-slate-700">{item.message}</td>
                  <td class="px-4 py-3 text-xs text-slate-500">{new Date(item.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</td>
                  <td class="px-4 py-3 text-right">
                    <button
                      class="text-slate-400 hover:text-red-600 p-1 rounded hover:bg-red-50 transition-colors"
                      onclick={() => handleDeleteNotification('student', item.id)}
                      title="Delete log"
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              {/each}
            {/if}
          </tbody>
        </table>
      {:else}
        <table class="w-full text-left text-sm text-slate-600">
          <thead class="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <tr>
              <th class="px-4 py-3">ID</th>
              <th class="px-4 py-3">Recipient Staff</th>
              <th class="px-4 py-3">Message</th>
              <th class="px-4 py-3">Sent At</th>
              <th class="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            {#if historyStaff.length === 0}
              <tr>
                <td colspan="5" class="text-center py-8 text-slate-400">No staff announcements sent yet.</td>
              </tr>
            {:else}
              {#each historyStaff as item}
                <tr class="hover:bg-slate-50/80 transition-colors">
                  <td class="px-4 py-3 text-xs font-mono text-slate-400">#{item.id}</td>
                  <td class="px-4 py-3 font-medium text-slate-800">{item.staff_name} <span class="text-xs text-slate-400">(@{item.staff_username})</span></td>
                  <td class="px-4 py-3 max-w-xs truncate text-slate-700">{item.message}</td>
                  <td class="px-4 py-3 text-xs text-slate-500">{new Date(item.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</td>
                  <td class="px-4 py-3 text-right">
                    <button
                      class="text-slate-400 hover:text-red-600 p-1 rounded hover:bg-red-50 transition-colors"
                      onclick={() => handleDeleteNotification('staff', item.id)}
                      title="Delete log"
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              {/each}
            {/if}
          </tbody>
        </table>
      {/if}
    </div>
  </div>
</div>
