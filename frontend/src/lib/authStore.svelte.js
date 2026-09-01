import { getToken, setToken, api } from './api.js';

let user = $state(JSON.parse(localStorage.getItem('user') || 'null'));
let isAuthenticated = $state(!!getToken());
let loading = $state(false);

export const auth = {
  get user() { return user; },
  get isAuthenticated() { return isAuthenticated; },
  get loading() { return loading; },

  async login(username, password) {
    loading = true;
    try {
      const data = await api.login(username, password);
      setToken(data.access);
      localStorage.setItem('user', JSON.stringify(data.user));
      user = data.user;
      isAuthenticated = true;
      return data;
    } finally {
      loading = false;
    }
  },

  logout() {
    setToken(null);
    localStorage.removeItem('user');
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
  }
};
