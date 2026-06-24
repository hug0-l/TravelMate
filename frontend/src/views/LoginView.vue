<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const email = ref("");
const password = ref("");
const error = ref("");

async function handleLogin() {
  try {
    error.value = "";
    await auth.login(email.value, password.value);
    router.push("/");
  } catch (e: any) {
    error.value = e.response?.data?.detail || "登入失敗，請重試";
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">
      <div class="mb-8 text-center">
        <h1 class="text-4xl">✈️</h1>
        <h2 class="mt-2 text-2xl font-bold text-gray-900">TravelMate</h2>
        <p class="mt-1 text-sm text-gray-500">登入你的旅程</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input
            v-model="email"
            type="email"
            required
            class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">密碼</label>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            placeholder="••••••••"
          />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          class="w-full rounded-lg bg-indigo-600 px-4 py-2 text-white font-medium hover:bg-indigo-700 transition"
        >
          登入
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-500">
        還沒有帳號？
        <router-link to="/register" class="font-medium text-indigo-600 hover:text-indigo-500">
          註冊
        </router-link>
      </p>
    </div>
  </div>
</template>
