<script>
  import { onMount } from 'svelte';
  import { auth } from './lib/authStore.svelte.js';
  import Navbar from './lib/components/Navbar.svelte';
  import Sidebar from './lib/components/Sidebar.svelte';
  import Login from './lib/views/Login.svelte';
  import Profile from './lib/views/Profile.svelte';

  // Admin Views
  import AdminDashboard from './lib/views/admin/AdminDashboard.svelte';
  import ManageStaff from './lib/views/admin/ManageStaff.svelte';
  import ManageStudents from './lib/views/admin/ManageStudents.svelte';
  import ManageCourses from './lib/views/admin/ManageCourses.svelte';
  import ManageSubjects from './lib/views/admin/ManageSubjects.svelte';
  import ManageSessions from './lib/views/admin/ManageSessions.svelte';
  import StudentLeaves from './lib/views/admin/StudentLeaves.svelte';
  import StaffLeaves from './lib/views/admin/StaffLeaves.svelte';
  import StudentFeedback from './lib/views/admin/StudentFeedback.svelte';
  import StaffFeedback from './lib/views/admin/StaffFeedback.svelte';
  import ViewAttendance from './lib/views/admin/ViewAttendance.svelte';

  // Staff Views
  import StaffDashboard from './lib/views/staff/StaffDashboard.svelte';
  import TakeAttendance from './lib/views/staff/TakeAttendance.svelte';
  import UpdateAttendance from './lib/views/staff/UpdateAttendance.svelte';
  import StaffApplyLeave from './lib/views/staff/ApplyLeave.svelte';
  import StaffSendFeedback from './lib/views/staff/SendFeedback.svelte';

  // Student Views
  import StudentDashboard from './lib/views/student/StudentDashboard.svelte';
  import StudentViewAttendance from './lib/views/student/ViewAttendance.svelte';
  import StudentApplyLeave from './lib/views/student/ApplyLeave.svelte';
  import StudentSendFeedback from './lib/views/student/SendFeedback.svelte';

  let currentView = $state('admin-dashboard');

  $effect(() => {
    if (auth.isAuthenticated && auth.user) {
      const uType = String(auth.user.user_type);
      if (uType === '1' && !currentView.startsWith('manage-') && !currentView.includes('leaves') && !currentView.includes('feedback') && currentView !== 'view-attendance' && currentView !== 'profile') {
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
  <div class="app-container">
    <Sidebar bind:currentView />
    <div class="main-content">
      <Navbar bind:currentView />

      <main class="page-container">
        {#if currentView === 'profile'}
          <Profile />

        <!-- Admin Views -->
        {:else if currentView === 'admin-dashboard'}
          <AdminDashboard bind:currentView />
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

        <!-- Staff Views -->
        {:else if currentView === 'staff-dashboard'}
          <StaffDashboard bind:currentView />
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

<style>
  .page-container {
    flex: 1;
    overflow-y: auto;
  }
</style>
