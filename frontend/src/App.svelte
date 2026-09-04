<script>
  import { onMount } from 'svelte';
  import { auth } from './lib/authStore.svelte.js';
  import Navbar from './lib/components/Navbar.svelte';
  import Sidebar from './lib/components/Sidebar.svelte';
  import Login from './lib/views/Login.svelte';
  import Profile from './lib/views/Profile.svelte';

  // Admin Views
  import AdminDashboard from './lib/views/admin/AdminDashboard.svelte';
  import BroadcastNotification from './lib/views/admin/BroadcastNotification.svelte';
  import ManageFees from './lib/views/admin/ManageFees.svelte';
  import ManageStaff from './lib/views/admin/ManageStaff.svelte';
  import ManageStudents from './lib/views/admin/ManageStudents.svelte';
  import ManageCourses from './lib/views/admin/ManageCourses.svelte';
  import ManageSubjects from './lib/views/admin/ManageSubjects.svelte';
  import ManageSessions from './lib/views/admin/ManageSessions.svelte';
  import ManageResults from './lib/views/admin/ManageResults.svelte';
  import StudentLeaves from './lib/views/admin/StudentLeaves.svelte';
  import StaffLeaves from './lib/views/admin/StaffLeaves.svelte';
  import StudentFeedback from './lib/views/admin/StudentFeedback.svelte';
  import StaffFeedback from './lib/views/admin/StaffFeedback.svelte';
  import ViewAttendance from './lib/views/admin/ViewAttendance.svelte';
  import ManageDocuments from './lib/views/admin/ManageDocuments.svelte';
  import ManageAssignments from './lib/views/staff/ManageAssignments.svelte';
  import ReportsCenter from './lib/views/admin/ReportsCenter.svelte';

  // Staff Views
  import StaffDashboard from './lib/views/staff/StaffDashboard.svelte';
  import StaffNotifications from './lib/views/staff/StaffNotifications.svelte';
  import StaffManageResults from './lib/views/staff/ManageResults.svelte';
  import TakeAttendance from './lib/views/staff/TakeAttendance.svelte';
  import UpdateAttendance from './lib/views/staff/UpdateAttendance.svelte';
  import StaffApplyLeave from './lib/views/staff/ApplyLeave.svelte';
  import StaffSendFeedback from './lib/views/staff/SendFeedback.svelte';

  // Student Views
  import StudentDashboard from './lib/views/student/StudentDashboard.svelte';
  import StudentNotifications from './lib/views/student/StudentNotifications.svelte';
  import StudentFees from './lib/views/student/StudentFees.svelte';
  import StudentDocuments from './lib/views/student/StudentDocuments.svelte';
  import StudentResults from './lib/views/student/StudentResults.svelte';
  import StudentAssignments from './lib/views/student/StudentAssignments.svelte';
  import StudentViewAttendance from './lib/views/student/ViewAttendance.svelte';
  import StudentApplyLeave from './lib/views/student/ApplyLeave.svelte';
  import StudentSendFeedback from './lib/views/student/SendFeedback.svelte';

  let currentView = $state('admin-dashboard');

  $effect(() => {
    if (auth.isAuthenticated && auth.user) {
      const uType = String(auth.user.user_type);
      if (uType === '1' && !currentView.startsWith('manage-') && !currentView.includes('leaves') && !currentView.includes('feedback') && currentView !== 'view-attendance' && currentView !== 'profile' && currentView !== 'broadcast-notifications' && currentView !== 'reports-center') {
        currentView = 'admin-dashboard';
      } else if (uType === '2' && currentView === 'admin-dashboard') {
        currentView = 'staff-dashboard';
      } else if (uType === '3' && currentView === 'admin-dashboard') {
        currentView = 'student-dashboard';
      }
    }
  });

  onMount(async () => {
    if (auth.isAuthenticated) {
      await auth.refreshUser();
    }
  });
</script>

{#if !auth.isAuthenticated || !auth.user}
  <Login />
{:else}
  <div class="flex h-screen overflow-hidden bg-slate-50 font-sans">
    <Sidebar bind:currentView />
    <div class="flex-1 flex flex-col min-w-0 overflow-y-auto bg-slate-50">
      <Navbar bind:currentView />

      <main class="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
        {#if currentView === 'profile'}
          <Profile />

        <!-- Admin Views -->
        {:else if currentView === 'admin-dashboard'}
          <AdminDashboard bind:currentView />
        {:else if currentView === 'broadcast-notifications'}
          <BroadcastNotification />
        {:else if currentView === 'manage-staff'}
          <ManageStaff />
        {:else if currentView === 'manage-students'}
          <ManageStudents />
        {:else if currentView === 'manage-courses'}
          <ManageCourses />
        {:else if currentView === 'manage-subjects'}
          <ManageSubjects />
        {:else if currentView === 'manage-sessions'}
          <ManageSessions />
        {:else if currentView === 'manage-results'}
          <ManageResults />
        {:else if currentView === 'manage-fees'}
          <ManageFees />
        {:else if currentView === 'manage-documents'}
          <ManageDocuments />
        {:else if currentView === 'manage-assignments'}
          <ManageAssignments />
        {:else if currentView === 'student-leaves'}
          <StudentLeaves />
        {:else if currentView === 'staff-leaves'}
          <StaffLeaves />
        {:else if currentView === 'student-feedback'}
          <StudentFeedback />
        {:else if currentView === 'staff-feedback'}
          <StaffFeedback />
        {:else if currentView === 'view-attendance'}
          <ViewAttendance />
        {:else if currentView === 'reports-center'}
          <ReportsCenter />

        <!-- Staff Views -->
        {:else if currentView === 'staff-dashboard'}
          <StaffDashboard bind:currentView />
        {:else if currentView === 'staff-notifications'}
          <StaffNotifications />
        {:else if currentView === 'staff-assignments'}
          <ManageAssignments />
        {:else if currentView === 'staff-results'}
          <StaffManageResults />
        {:else if currentView === 'take-attendance'}
          <TakeAttendance />
        {:else if currentView === 'update-attendance'}
          <UpdateAttendance />
        {:else if currentView === 'apply-leave'}
          <StaffApplyLeave />
        {:else if currentView === 'send-feedback'}
          <StaffSendFeedback />

        <!-- Student Views -->
        {:else if currentView === 'student-dashboard'}
          <StudentDashboard bind:currentView />
        {:else if currentView === 'student-notifications'}
          <StudentNotifications />
        {:else if currentView === 'student-assignments'}
          <StudentAssignments />
        {:else if currentView === 'student-fees'}
          <StudentFees />
        {:else if currentView === 'student-documents'}
          <StudentDocuments />
        {:else if currentView === 'student-results'}
          <StudentResults />
        {:else if currentView === 'student-attendance'}
          <StudentViewAttendance />
        {:else if currentView === 'student-apply-leave'}
          <StudentApplyLeave />
        {:else if currentView === 'student-send-feedback'}
          <StudentSendFeedback />
        {/if}
      </main>
    </div>
  </div>
{/if}
