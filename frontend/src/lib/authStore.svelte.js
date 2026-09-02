import { getToken, getRefreshToken, setTokens, clearTokens, silentRefreshToken, api } from './api.js';

let user = $state(JSON.parse(localStorage.getItem('user') || 'null'));
let isAuthenticated = $state(!!getToken());
let loading = $state(false);

// Global listener for session expiry events triggered by api.js
if (typeof window !== 'undefined') {
  window.addEventListener('auth:expired', () => {
    user = null;
    isAuthenticated = false;
  });
}

export const auth = {
  get user() { return user; },
  get isAuthenticated() { return isAuthenticated; },
  get loading() { return loading; },

  async login(username, password) {
    loading = true;
    try {
      const data = await api.login(username, password);
      setTokens(data.access, data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
      user = data.user;
      isAuthenticated = true;
      return data;
    } finally {
      loading = false;
    }
  },

  logout() {
    clearTokens();
    user = null;
    isAuthenticated = false;
  },

  async refreshUser() {
    if (!getToken()) return;
    try {
      const me = await api.getMe();
      user = { ...user, ...me };
      localStorage.setItem('user', JSON.stringify(user));
    } catch (err) {
      console.error('Failed to fetch user:', err);
    }
  },

  async keepAlive() {
    if (!getRefreshToken()) return;
    try {
      await silentRefreshToken();
    } catch (err) {
      console.warn('Keepalive refresh failed:', err);
    }
  }
};

