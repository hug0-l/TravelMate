<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const name = ref("");
const email = ref("");
const password = ref("");
const error = ref("");

async function handleRegister() {
  try {
    error.value = "";
    await auth.register(email.value, name.value, password.value);
    router.push("/");
  } catch (e: any) {
    error.value = e.response?.data?.detail || "註冊失敗，請重試";
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">
      <div class="mb-8 text-center">
        <h1 class="text-4xl">✈️</h1>
        <h2 class="mt-2 text-2xl font-bold text-gray-900">加入 TravelMate</h2>
        <p class="mt-1 text-sm text-gray-500">建立你的第一個旅程</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">姓名</label>
          <input
            v-model="name"
            type="text"
            required
            class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            placeholder="你的名字"
          />
        </div>
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
            minlength="6"
            class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            placeholder="至少 6 碼"
          />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          class="w-full rounded-lg bg-indigo-600 px-4 py-2 text-white font-medium hover:bg-indigo-700 transition"
        >
          註冊
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-500">
        已經有帳號了？
        <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">
          登入
        </router-link>
      </p>
    </div>
  </div>
</template>
