<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../api/client";

const auth = useAuthStore();
const router = useRouter();

interface Stats {
  total_users: number;
  total_trips: number;
  total_activities: number;
  total_expenses: number;
  total_memories: number;
}

interface UserRow {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
  created_at: string | null;
}

interface TripRow {
  id: string;
  title: string;
  created_at: string | null;
}

const stats = ref<Stats | null>(null);
const users = ref<UserRow[]>([]);
const recentTrips = ref<TripRow[]>([]);
const loading = ref(false);
const error = ref("");
const activeSection = ref<"stats" | "users" | "trips">("stats");

async function fetchStats() {
  loading.value = true;
  error.value = "";
  try {
    const [s, u, t] = await Promise.all([
      api.get("/admin/stats"),
      api.get("/admin/users"),
      api.get("/admin/trips/recent"),
    ]);
    stats.value = s.data;
    users.value = u.data;
    recentTrips.value = t.data;
  } catch (e: any) {
    if (e.response?.status === 403) {
      error.value = "⚠️ 僅管理員可存取";
    } else {
      error.value = "⚠️ 無法載入管理資料";
    }
  } finally {
    loading.value = false;
  }
}

async function toggleAdmin(userId: string) {
  try {
    await api.put(`/admin/users/${userId}/toggle-admin`);
    await fetchStats();
  } catch {
    error.value = "⚠️ 操作失敗";
  }
}

onMounted(fetchStats);
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-gradient-to-r from-indigo-700 to-purple-700 shadow-lg">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div class="flex items-center gap-3">
          <button @click="router.push('/')" class="text-white/80 hover:text-white text-lg">←</button>
          <h1 class="text-lg font-bold text-white">⚙️ 管理後台</h1>
        </div>
        <span class="text-sm text-indigo-200">{{ auth.user?.name }}</span>
      </div>
    </header>

    <div v-if="error && !loading" class="mx-auto max-w-md mt-20 text-center">
      <p class="text-red-600 text-lg">{{ error }}</p>
      <button @click="router.push('/')" class="mt-4 text-indigo-600 hover:underline">返回首頁</button>
    </div>

    <div v-else class="mx-auto max-w-6xl px-4 py-6">
      <!-- Tab bar -->
      <div class="flex gap-2 mb-6">
        <button @click="activeSection = 'stats'" :class="['px-4 py-2 rounded-lg text-sm font-medium transition', activeSection === 'stats' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50']">📊 系統概覽</button>
        <button @click="activeSection = 'users'" :class="['px-4 py-2 rounded-lg text-sm font-medium transition', activeSection === 'users' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50']">👥 用戶管理</button>
        <button @click="activeSection = 'trips'" :class="['px-4 py-2 rounded-lg text-sm font-medium transition', activeSection === 'trips' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50']">📅 近期行程</button>
      </div>

      <div v-if="loading" class="py-12 text-center text-gray-400 animate-pulse">載入中...</div>

      <!-- Stats -->
      <div v-if="!loading && activeSection === 'stats' && stats" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div class="rounded-xl bg-white p-6 shadow-sm"><p class="text-xs text-gray-500">用戶總數</p><p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total_users }}</p></div>
        <div class="rounded-xl bg-white p-6 shadow-sm"><p class="text-xs text-gray-500">行程總數</p><p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total_trips }}</p></div>
        <div class="rounded-xl bg-white p-6 shadow-sm"><p class="text-xs text-gray-500">活動總數</p><p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total_activities }}</p></div>
        <div class="rounded-xl bg-white p-6 shadow-sm"><p class="text-xs text-gray-500">開銷總數</p><p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total_expenses }}</p></div>
        <div class="rounded-xl bg-white p-6 shadow-sm"><p class="text-xs text-gray-500">回憶總數</p><p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total_memories }}</p></div>
      </div>

      <!-- Users -->
      <div v-if="!loading && activeSection === 'users'" class="space-y-2">
        <div v-for="u in users" :key="u.id" class="flex items-center justify-between rounded-lg bg-white px-4 py-3 shadow-sm">
          <div>
            <p class="text-sm font-medium text-gray-900">{{ u.name }}</p>
            <p class="text-xs text-gray-400">{{ u.email }}</p>
          </div>
          <div class="flex items-center gap-3">
            <span :class="['rounded px-2 py-0.5 text-xs font-medium', u.is_admin ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600']">{{ u.is_admin ? '管理員' : '一般' }}</span>
            <button @click="toggleAdmin(u.id)" class="text-xs text-indigo-600 hover:underline">{{ u.is_admin ? '取消管理員' : '設為管理員' }}</button>
          </div>
        </div>
      </div>

      <!-- Trips -->
      <div v-if="!loading && activeSection === 'trips'" class="space-y-2">
        <div v-for="t in recentTrips" :key="t.id" class="rounded-lg bg-white px-4 py-3 shadow-sm">
          <p class="text-sm font-medium text-gray-900">{{ t.title }}</p>
          <p class="text-xs text-gray-400">{{ t.created_at }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
