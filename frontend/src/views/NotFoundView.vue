<script setup lang="ts">
import { useRouter } from "vue-router";
import { onMounted } from "vue";
const router = useRouter();
onMounted(() => { document.title = "404 - TravelMate"; });
</script>
<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
    <div class="text-center">
      <p class="text-8xl mb-4">🗺️</p>
      <h1 class="text-4xl font-bold text-gray-900 mb-2">404</h1>
      <p class="text-gray-500 mb-8">這個頁面不存在，或者已經消失了...</p>
      <button @click="router.push('/')" class="rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 px-6 py-3 text-sm font-semibold text-white shadow-md hover:shadow-lg transition-all">
        ← 回首頁
      </button>
    </div>
  </div>
</template>
