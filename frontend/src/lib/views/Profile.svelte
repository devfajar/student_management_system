<script>
  import { auth } from '../authStore.svelte.js';
  import { api } from '../api.js';
  import { User, Save, CheckCircle, AlertCircle, Loader2, Camera, UploadCloud } from 'lucide-svelte';

  let first_name = $state(auth.user?.first_name || '');
  let last_name = $state(auth.user?.last_name || '');
  let address = $state(auth.user?.profile?.address || '');
  let password = $state('');
  let profilePicFile = $state(null);
  let profilePicPreview = $state(auth.user?.profile?.profile_pic || '');
  let success = $state('');
  let error = $state('');
  let loading = $state(false);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      profilePicFile = file;
      profilePicPreview = URL.createObjectURL(file);
    }
  }

  async function handleSave(e) {
    e.preventDefault();
    success = '';
    error = '';
    loading = true;
    try {
      const formData = new FormData();
      formData.append('first_name', first_name);
      formData.append('last_name', last_name);
      if (password) formData.append('password', password);
      if (address) formData.append('address', address);
      if (profilePicFile) formData.append('profile_pic', profilePicFile);

      await api.updateProfile(formData);
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

<div class="max-w-2xl mx-auto space-y-6 animate-in fade-in duration-200">
  <div>
    <h1 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2.5">
      <User class="text-blue-600" size={28} />
      Account Settings & Profile
    </h1>
    <p class="text-sm text-slate-500 mt-1">Manage your credentials, contact information, and avatar photo</p>
  </div>

  {#if success}
    <div class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl flex items-center gap-2 text-sm shadow-sm">
      <CheckCircle size={18} />
      <span>{success}</span>
    </div>
  {/if}

  {#if error}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-2 text-sm shadow-sm">
      <AlertCircle size={18} />
      <span>{error}</span>
    </div>
  {/if}

  <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm">
    <form onsubmit={handleSave} class="space-y-6">
      <!-- Avatar Section -->
      <div class="flex flex-col sm:flex-row items-center gap-6 pb-6 border-b border-slate-100">
        <div class="relative group">
          <div class="w-24 h-24 rounded-full overflow-hidden bg-slate-100 border-2 border-slate-200 flex items-center justify-center text-slate-400 font-bold text-2xl shadow-inner">
            {#if profilePicPreview}
              <img src={profilePicPreview} alt="Avatar" class="w-full h-full object-cover" />
            {:else}
              <span>{auth.user?.username?.charAt(0)?.toUpperCase()}</span>
            {/if}
          </div>
          <label class="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center cursor-pointer shadow-md transition-all">
            <Camera size={15} />
            <input type="file" accept="image/*" class="hidden" onchange={handleFileChange} />
          </label>
        </div>
        <div class="space-y-1 text-center sm:text-left">
          <h3 class="font-bold text-slate-800 text-base">{auth.user?.first_name} {auth.user?.last_name}</h3>
          <p class="text-xs text-slate-500 font-medium">@{auth.user?.username} &bull; {auth.user?.email}</p>
          <p class="text-[11px] text-slate-400">Click camera button to upload PNG, JPG, or GIF (max 5MB)</p>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Username</label>
          <input type="text" class="w-full px-3.5 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-sm text-slate-500 cursor-not-allowed font-medium" value={auth.user?.username} disabled />
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Email Address</label>
          <input type="email" class="w-full px-3.5 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-sm text-slate-500 cursor-not-allowed font-medium" value={auth.user?.email} disabled />
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">First Name</label>
          <input type="text" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500" bind:value={first_name} />
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Last Name</label>
          <input type="text" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500" bind:value={last_name} />
        </div>
      </div>

      {#if auth.user?.user_type !== '1'}
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Residential Address</label>
          <input type="text" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500" bind:value={address} />
        </div>
      {/if}

      <div>
        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Change Password</label>
        <input type="password" placeholder="Leave blank to retain current password" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500" bind:value={password} />
      </div>

      <div class="pt-2">
        <button type="submit" class="flex items-center justify-center gap-2 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all" disabled={loading}>
          {#if loading}
            <Loader2 size={16} class="animate-spin" />
            <span>Saving Changes...</span>
          {:else}
            <Save size={16} />
            <span>Save Profile</span>
          {/if}
        </button>
      </div>
    </form>
  </div>
</div>

