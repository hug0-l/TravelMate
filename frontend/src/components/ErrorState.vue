<script setup lang="ts">
defineProps<{
  message?: string
  retryText?: string
}>()

const emit = defineEmits<{
  retry: []
}>()
</script>

<template>
  <div class="flex items-center justify-center py-16">
    <div class="w-full max-w-md rounded-2xl border border-red-100 bg-red-50/50 px-8 py-12 text-center shadow-sm">
      <div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-red-100 text-5xl">
        ⚠️
      </div>
      <h3 class="mb-2 text-xl font-bold text-red-800">發生錯誤</h3>
      <p class="mb-6 text-sm text-red-600">{{ message || '無法載入資料，請稍後再試' }}</p>
      <button
        v-if="retryText"
        @click="emit('retry')"
        class="inline-flex items-center gap-1.5 rounded-lg bg-red-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md hover:bg-red-700 transition-all"
      >
        {{ retryText || '重試' }}
      </button>
    </div>
  </div>
</template>
