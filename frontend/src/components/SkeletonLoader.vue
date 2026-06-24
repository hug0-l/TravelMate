<script setup lang="ts">
defineProps<{
  lines?: number
  hasAvatar?: boolean
  hasImage?: boolean
  class?: string
}>()
</script>

<template>
  <div :class="['animate-pulse space-y-3', $props.class]">
    <div v-if="hasAvatar" class="flex items-center gap-3">
      <div class="h-10 w-10 rounded-full bg-gradient-to-r from-indigo-200 via-purple-200 to-indigo-200"></div>
      <div class="flex-1 space-y-2">
        <div class="h-3 w-1/3 rounded bg-gradient-to-r from-indigo-200 via-purple-200 to-indigo-200"></div>
        <div class="h-3 w-1/2 rounded bg-gradient-to-r from-indigo-100 via-purple-100 to-indigo-100"></div>
      </div>
    </div>
    <div v-if="hasImage" class="h-40 w-full rounded-xl bg-gradient-to-r from-indigo-200 via-purple-200 to-indigo-200"></div>
    <div v-for="i in lines || 3" :key="i" class="h-3 rounded bg-gradient-to-r from-indigo-200 via-purple-200 to-indigo-200"
      :style="{ width: i === (lines || 3) ? '60%' : '100%' }">
    </div>
  </div>
</template>
