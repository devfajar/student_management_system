<script>
  import { auth } from '../authStore.svelte.js';
  import { api } from '../api.js';
  import { User, Save, CheckCircle, AlertCircle, Loader2 } from 'lucide-svelte';

  let first_name = $state(auth.user?.first_name || '');
  let last_name = $state(auth.user?.last_name || '');
  let address = $state(auth.user?.profile?.address || '');
  let password = $state('');
  let success = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleSave(e) {
    e.preventDefault();
    success = '';
    error = '';
    loading = true;
    try {
      const payload = { first_name, last_name };
      if (password) payload.password = password;
      if (address) payload.address = address;
      await api.updateProfile(payload);
      await auth.refreshUser();
      success = 'Profile updated successfully!';
      password = '';
    } catch (err) {
      error = err.message || 'Failed to update profile';
    } finally {
      loading = false;
    }
  }
</script>

<div class="content-body">
  <div class="card" style="max-width: 650px; margin: 0 auto;">
    <div class="card-header">
      <h2 class="card-title">
        <User size={20} color="#3b82f6" />
        Edit Profile
      </h2>
    </div>

    {#if success}
      <div class="alert alert-success">
        <CheckCircle size={16} />
        <span>{success}</span>
      </div>
    {/if}

    {#if error}
      <div class="alert alert-danger">
        <AlertCircle size={16} />
        <span>{error}</span>
      </div>
    {/if}

    <form onsubmit={handleSave}>
      <div class="form-group">
        <label class="form-label" for="profile-username">Username</label>
        <input id="profile-username" type="text" class="form-control" value={auth.user?.username} disabled />
      </div>

      <div class="form-group">
        <label class="form-label" for="profile-email">Email</label>
        <input id="profile-email" type="email" class="form-control" value={auth.user?.email} disabled />
      </div>

      <div class="row-2">
        <div class="form-group">
          <label class="form-label" for="profile-fn">First Name</label>
          <input id="profile-fn" type="text" class="form-control" bind:value={first_name} />
        </div>
        <div class="form-group">
          <label class="form-label" for="profile-ln">Last Name</label>
          <input id="profile-ln" type="text" class="form-control" bind:value={last_name} />
        </div>
      </div>

      {#if auth.user?.user_type !== '1'}
        <div class="form-group">
          <label class="form-label" for="profile-address">Address</label>
          <input id="profile-address" type="text" class="form-control" bind:value={address} />
        </div>
      {/if}

      <div class="form-group">
        <label class="form-label" for="profile-pass">Change Password (leave blank to keep current)</label>
        <input id="profile-pass" type="password" class="form-control" placeholder="New password" bind:value={password} />
      </div>

      <button type="submit" class="btn btn-primary" disabled={loading}>
        {#if loading}
          <Loader2 size={16} class="animate-spin" />
          <span>Saving...</span>
        {:else}
          <Save size={16} />
          <span>Save Changes</span>
        {/if}
      </button>
    </form>
  </div>
</div>

<style>
  .row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
</style>
