<script setup lang="ts">
import { useToast } from "../composables/useToast";

const { toasts, remove } = useToast();

const iconMap: Record<string, string> = {
  success: "✅",
  error: "❌",
  info: "ℹ️",
  warning: "⚠️",
};
</script>

<template>
  <TransitionGroup
    name="toast"
    tag="div"
    class="fixed bottom-20 md:bottom-4 left-4 z-[100] space-y-2"
  >
    <div
      v-for="toast in toasts"
      :key="toast.id"
      :class="[
        'rounded-xl shadow-lg border px-4 py-3 text-sm flex items-center gap-2',
        toast.type === 'success' && 'bg-green-50 border-green-200 text-green-800',
        toast.type === 'error' && 'bg-red-50 border-red-200 text-red-800',
        toast.type === 'info' && 'bg-blue-50 border-blue-200 text-blue-800',
        toast.type === 'warning' && 'bg-amber-50 border-amber-200 text-amber-800',
      ]"
    >
      <span>{{ iconMap[toast.type] }}</span>
      <span class="flex-1">{{ toast.message }}</span>
      <button @click="remove(toast.id)" class="ml-auto text-current opacity-50 hover:opacity-100">
        ✕
      </button>
    </div>
  </TransitionGroup>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>
