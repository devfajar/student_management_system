<script>
  import { auth } from '../authStore.svelte.js';
  import {
    LayoutDashboard, Users, UserCheck, GraduationCap,
    BookOpen, Calendar, Clock, MessageSquare,
    ClipboardCheck, FileEdit, Send, CheckCircle2, User, Award,
    Megaphone, Bell, CircleDollarSign, FileCheck, FileText, FileSpreadsheet,
    CreditCard
  } from 'lucide-svelte';

  let { currentView = $bindable() } = $props();

  const userType = $derived(String(auth.user?.user_type || '1'));
</script>

<aside class="w-64 bg-slate-900 text-slate-400 h-screen flex flex-col flex-shrink-0 overflow-y-auto border-r border-slate-800 selection:bg-blue-600 selection:text-white">
  <!-- Brand Logo -->
  <div class="h-16 px-6 flex items-center border-b border-slate-800/80 gap-3">
    <div class="w-9 h-9 rounded-xl bg-blue-600/15 text-blue-500 border border-blue-500/20 flex items-center justify-center">
      <GraduationCap size={22} />
    </div>
    <div>
      <h2 class="text-base font-bold text-white tracking-tight leading-tight">SMS Portal</h2>
      <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Management Hub</p>
    </div>
  </div>

  <nav class="p-3.5 space-y-1">
    {#if userType === '1'}
      <!-- Admin Nav -->
      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-3 pb-1 uppercase">Overview</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'admin-dashboard' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'admin-dashboard'}
      >
        <LayoutDashboard size={17} />
        <span>Dashboard</span>
      </button>

      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Academic Operations</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'broadcast-notifications' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'broadcast-notifications'}
      >
        <Megaphone size={17} />
        <span>Campus Broadcasts</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-results' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-results'}
      >
        <Award size={17} />
        <span>Exam Results</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-fees' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-fees'}
      >
        <CircleDollarSign size={17} />
        <span>Student Fees</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-payroll' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-payroll'}
      >
        <CreditCard size={17} />
        <span>Staff Payroll</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-assignments' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-assignments'}
      >
        <BookOpen size={17} />
        <span>Coursework & Assignments</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-documents' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-documents'}
      >
        <FileCheck size={17} />
        <span>Student Documents</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'view-attendance' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'view-attendance'}
      >
        <ClipboardCheck size={17} />
        <span>View Attendance</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'reports-center' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'reports-center'}
      >
        <FileSpreadsheet size={17} />
        <span>Reports & Exports</span>
      </button>

      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Institution Setup</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-staff' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-staff'}
      >
        <UserCheck size={17} />
        <span>Manage Staff</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-students' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-students'}
      >
        <Users size={17} />
        <span>Manage Students</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-courses' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-courses'}
      >
        <GraduationCap size={17} />
        <span>Manage Courses</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-subjects' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-subjects'}
      >
        <BookOpen size={17} />
        <span>Manage Subjects</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'manage-sessions' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'manage-sessions'}
      >
        <Calendar size={17} />
        <span>Session Years</span>
      </button>

      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Leaves & Feedback</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-leaves' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-leaves'}
      >
        <Clock size={17} />
        <span>Student Leaves</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'staff-leaves' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'staff-leaves'}
      >
        <Clock size={17} />
        <span>Staff Leaves</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-feedback' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-feedback'}
      >
        <MessageSquare size={17} />
        <span>Student Feedback</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'staff-feedback' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'staff-feedback'}
      >
        <MessageSquare size={17} />
        <span>Staff Feedback</span>
      </button>

    {:else if userType === '2'}
      <!-- Staff Nav -->
      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-3 pb-1 uppercase">Main</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'staff-dashboard' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'staff-dashboard'}
      >
        <LayoutDashboard size={17} />
        <span>Dashboard</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'staff-notifications' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'staff-notifications'}
      >
        <Bell size={17} />
        <span>Announcements</span>
      </button>

      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Academic</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'staff-assignments' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'staff-assignments'}
      >
        <BookOpen size={17} />
        <span>Assignments</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'staff-results' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'staff-results'}
      >
        <Award size={17} />
        <span>Add / Edit Results</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'take-attendance' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'take-attendance'}
      >
        <ClipboardCheck size={17} />
        <span>Take Attendance</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'update-attendance' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'update-attendance'}
      >
        <FileEdit size={17} />
        <span>Update Attendance</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'reports-center' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'reports-center'}
      >
        <FileSpreadsheet size={17} />
        <span>Reports & Exports</span>
      </button>

      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Requests & Support</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'apply-leave' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'apply-leave'}
      >
        <Clock size={17} />
        <span>Apply Leave</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'send-feedback' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'send-feedback'}
      >
        <Send size={17} />
        <span>Send Feedback</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'staff-payslips' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'staff-payslips'}
      >
        <CreditCard size={17} />
        <span>My Salary & Payslips</span>
      </button>

    {:else if userType === '3'}
      <!-- Student Nav -->
      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-3 pb-1 uppercase">Main</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-dashboard' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-dashboard'}
      >
        <LayoutDashboard size={17} />
        <span>Dashboard</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-notifications' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-notifications'}
      >
        <Bell size={17} />
        <span>Announcements</span>
      </button>

      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Academic</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-assignments' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-assignments'}
      >
        <BookOpen size={17} />
        <span>My Coursework</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-results' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-results'}
      >
        <Award size={17} />
        <span>Exam Results</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-attendance' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-attendance'}
      >
        <CheckCircle2 size={17} />
        <span>View Attendance</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-fees' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-fees'}
      >
        <CircleDollarSign size={17} />
        <span>Fee Statement</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-documents' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-documents'}
      >
        <FileText size={17} />
        <span>My Documents</span>
      </button>

      <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Requests & Support</div>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-apply-leave' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-apply-leave'}
      >
        <Clock size={17} />
        <span>Apply Leave</span>
      </button>
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'student-send-feedback' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
        onclick={() => currentView = 'student-send-feedback'}
      >
        <Send size={17} />
        <span>Send Feedback</span>
      </button>
    {/if}

    <div class="text-[10px] font-bold tracking-wider text-slate-500 px-3 pt-4 pb-1 uppercase">Account</div>
    <button
      class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all {currentView === 'profile' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
      onclick={() => currentView = 'profile'}
    >
      <User size={17} />
      <span>My Profile</span>
    </button>
  </nav>
</aside>

