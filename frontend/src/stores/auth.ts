import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi } from "../api/client";
import type { User } from "../types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem("token"));
  const refreshToken = ref<string | null>(localStorage.getItem("refresh_token"));

  const isLoggedIn = computed(() => !!token.value);

  function _saveTokens(access: string, refresh: string, userData: User) {
    token.value = access;
    refreshToken.value = refresh;
    user.value = userData;
    localStorage.setItem("token", access);
    localStorage.setItem("refresh_token", refresh);
    localStorage.setItem("user", JSON.stringify(userData));
  }

  async function login(email: string, password: string) {
    const res = await authApi.login({ email, password });
    _saveTokens(res.data.access_token, res.data.refresh_token || "", {
      id: res.data.user_id, email, name: res.data.name,
    });
  }

  async function register(email: string, name: string, password: string) {
    const res = await authApi.register({ email, name, password });
    _saveTokens(res.data.access_token, res.data.refresh_token || "", {
      id: res.data.user_id, email, name: res.data.name,
    });
  }

  async function refresh() {
    if (!refreshToken.value) return false;
    try {
      const res = await authApi.refresh(refreshToken.value);
      _saveTokens(res.data.access_token, res.data.refresh_token || "", user.value!);
      return true;
    } catch {
      logout();
      return false;
    }
  }

  function logout() {
    token.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }

  function restoreSession() {
    const stored = localStorage.getItem("user");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Validate shape to prevent injected data
        if (parsed && typeof parsed === "object" && parsed.id && parsed.name) {
          user.value = parsed as User;
        }
      } catch {
        localStorage.removeItem("user");
      }
    }
  }

  return { user, token, refreshToken, isLoggedIn, login, register, refresh, logout, restoreSession };
});
