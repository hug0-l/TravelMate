<script setup lang="ts">
defineProps<{
  icon?: string
  title?: string
  description?: string
  actionText?: string
}>()

const emit = defineEmits<{
  action: []
}>()
</script>

<template>
  <div class="flex items-center justify-center py-16">
    <div class="w-full max-w-md rounded-2xl border border-dashed border-gray-200 bg-white/50 px-8 py-12 text-center shadow-sm">
      <div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-indigo-50 text-5xl">
        {{ icon || '📭' }}
      </div>
      <h3 class="mb-2 text-xl font-bold text-gray-800">{{ title || '尚無資料' }}</h3>
      <p class="mb-6 text-sm text-gray-500">{{ description || '這裡還沒有任何內容' }}</p>
      <button
        v-if="actionText"
        @click="emit('action')"
        class="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md hover:shadow-lg hover:from-indigo-500 hover:to-indigo-400 transition-all"
      >
        {{ actionText }}
      </button>
    </div>
  </div>
</template>
