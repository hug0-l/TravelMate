<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";

const router = useRouter();
const tripId = ref("");
const joinCode = ref("");
const nickname = ref("");
const errorMsg = ref("");
const loading = ref(false);
const tripTitle = ref("");

async function lookupTrip() {
  if (tripId.value.length < 5) return;
  try {
    const res = await api.get(`/trips/${tripId.value}/join-info`);
    tripTitle.value = res.data.title;
  } catch {
    tripTitle.value = "";
  }
}

async function handleJoin() {
  if (!tripId.value || !joinCode.value || !nickname.value) return;
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.post("/trips/join", {
      trip_id: tripId.value,
      join_code: joinCode.value,
      nickname: nickname.value,
    });
    localStorage.setItem("guest_token", res.data.access_token);
    localStorage.setItem("guest_nickname", nickname.value);
    localStorage.setItem("guest_trip_id", tripId.value);
    router.push(`/trips/${tripId.value}`);
  } catch (e: any) {
    errorMsg.value = e.response?.data?.detail || "加入失敗，請檢查資訊";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-600 px-4">
    <div class="w-full max-w-sm rounded-2xl bg-white p-8 shadow-xl">
      <h1 class="text-2xl font-bold text-gray-900 text-center mb-2">✈️ 加入行程</h1>
      <p class="text-sm text-gray-500 text-center mb-6">不需要註冊，輸入邀請碼即可加入</p>

      <form @submit.prevent="handleJoin" class="space-y-4">
        <div>
          <label class="block text-xs text-gray-500 mb-1">行程 ID</label>
          <input v-model="tripId" @input="lookupTrip" placeholder="輸入行程 ID" required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500" />
          <p v-if="tripTitle" class="mt-1 text-xs text-green-600">✅ 找到行程：{{ tripTitle }}</p>
        </div>

        <div>
          <label class="block text-xs text-gray-500 mb-1">加入碼</label>
          <input v-model="joinCode" placeholder="6 位數字加入碼" required maxlength="6"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500" />
        </div>

        <div>
          <label class="block text-xs text-gray-500 mb-1">暱稱</label>
          <input v-model="nickname" placeholder="顯示名稱" required maxlength="20"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500" />
        </div>

        <p v-if="errorMsg" class="text-xs text-red-600">{{ errorMsg }}</p>

        <button type="submit" :disabled="loading"
          class="w-full rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 py-2.5 text-sm font-semibold text-white shadow-md hover:shadow-lg transition-all disabled:opacity-50">
          {{ loading ? '加入中...' : '🚀 加入行程' }}
        </button>
      </form>

      <p class="mt-6 text-center text-xs text-gray-400">
        已有帳號？<router-link to="/login" class="text-indigo-600 hover:underline">登入</router-link>
      </p>
    </div>
  </div>
</template>
