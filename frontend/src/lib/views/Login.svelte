<script>
  import { auth } from '../authStore.svelte.js';
  import { GraduationCap, Lock, User, AlertCircle, Loader2 } from 'lucide-svelte';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleLogin(e) {
    e.preventDefault();
    error = '';
    loading = true;
    try {
      await auth.login(username, password);
    } catch (err) {
      error = err.message || 'Login failed. Please check credentials.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="login-wrapper">
  <div class="login-box">
    <div class="login-header">
      <div class="logo-circle">
        <GraduationCap size={32} color="#3b82f6" />
      </div>
      <h2>Student Management</h2>
      <p>Sign in to your account</p>
    </div>

    {#if error}
      <div class="alert alert-danger">
        <AlertCircle size={16} />
        <span>{error}</span>
      </div>
    {/if}

    <form onsubmit={handleLogin} class="login-form">
      <div class="form-group">
        <label for="username" class="form-label">Username or Email</label>
        <div class="input-icon-wrapper">
          <User size={16} class="input-icon" />
          <input
            id="username"
            type="text"
            class="form-control with-icon"
            placeholder="Enter username or email"
            bind:value={username}
            required
            autocomplete="username"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="password" class="form-label">Password</label>
        <div class="input-icon-wrapper">
          <Lock size={16} class="input-icon" />
          <input
            id="password"
            type="password"
            class="form-control with-icon"
            placeholder="Enter password"
            bind:value={password}
            required
            autocomplete="current-password"
          />
        </div>
      </div>

      <button type="submit" class="btn btn-primary btn-block py-2" disabled={loading}>
        {#if loading}
          <Loader2 size={16} class="animate-spin" />
          <span>Signing in...</span>
        {:else}
          <span>Sign In</span>
        {/if}
      </button>
    </form>

    <div class="demo-credentials">
      <p><strong>Demo Admin:</strong> <code>admin</code> / <code>admin123</code></p>
    </div>
  </div>
</div>

<style>
  .login-wrapper {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 20px;
  }

  .login-box {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border);
    max-width: 420px;
    width: 100%;
    padding: 36px 32px;
  }

  .login-header {
    text-align: center;
    margin-bottom: 28px;
  }

  .logo-circle {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background-color: var(--primary-light);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
  }

  .login-header h2 {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 4px;
  }

  .login-header p {
    font-size: 13px;
    color: var(--text-muted);
  }

  .login-form {
    margin-bottom: 20px;
  }

  .input-icon-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  :global(.input-icon) {
    position: absolute;
    left: 12px;
    color: #94a3b8;
    pointer-events: none;
  }

  .form-control.with-icon {
    padding-left: 38px;
  }

  .btn-block {
    width: 100%;
    font-size: 15px;
    font-weight: 600;
    margin-top: 8px;
  }

  .demo-credentials {
    background: #f8fafc;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    padding: 10px 14px;
    text-align: center;
    font-size: 12px;
    color: var(--text-muted);
  }

  .demo-credentials code {
    background: #e2e8f0;
    padding: 2px 6px;
    border-radius: 4px;
    color: #0f172a;
    font-weight: 600;
  }

  :global(.animate-spin) {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
