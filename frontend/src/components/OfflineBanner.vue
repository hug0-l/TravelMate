<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { syncQueue } from "../sync";

export type ConnectionStatus = "online" | "offline" | "syncing";

const connectionStatus = ref<ConnectionStatus>(
  navigator.onLine ? "online" : "offline"
);
const pendingCount = ref(0);
let pollTimer: ReturnType<typeof setInterval> | null = null;

async function updatePendingCount() {
  pendingCount.value = await syncQueue.getPendingCount();
}

function handleOnline() {
  connectionStatus.value = "online";
  syncQueue.flush().then(() => updatePendingCount());
}

function handleOffline() {
  connectionStatus.value = "offline";
}

async function handleSync() {
  connectionStatus.value = "syncing";
  await syncQueue.flush();
  await updatePendingCount();
  connectionStatus.value = "online";
}

const isVisible = computed(() => {
  if (connectionStatus.value === "offline") return true;
  if (connectionStatus.value === "syncing") return true;
  return pendingCount.value > 0;
});

const bannerClass = computed(() => {
  switch (connectionStatus.value) {
    case "offline":
      return "bg-amber-50 border-amber-200 text-amber-800";
    case "syncing":
      return "bg-indigo-50 border-indigo-200 text-indigo-800";
    default:
      return "bg-blue-50 border-blue-200 text-blue-800";
  }
});

const iconText = computed(() => {
  switch (connectionStatus.value) {
    case "offline":
      return "⚠️";
    case "syncing":
      return "🔄";
    default:
      return "🔄";
  }
});

const messageText = computed(() => {
  switch (connectionStatus.value) {
    case "offline":
      return "您目前處於離線狀態，變更將在恢復連線後同步";
    case "syncing":
      return "正在同步中...";
    default:
      return `有 ${pendingCount.value} 筆變更待同步`;
  }
});

onMounted(() => {
  window.addEventListener("online", handleOnline);
  window.addEventListener("offline", handleOffline);
  updatePendingCount();
  pollTimer = setInterval(updatePendingCount, 30_000);
});

onUnmounted(() => {
  window.removeEventListener("online", handleOnline);
  window.removeEventListener("offline", handleOffline);
  if (pollTimer !== null) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
});
</script>

<template>
  <Transition name="slide">
    <div
      v-if="isVisible"
      :class="bannerClass"
      class="fixed left-0 right-0 top-0 z-40 flex items-center justify-center gap-2 border-b px-4 py-2.5 text-sm font-medium shadow-sm"
    >
      <span>{{ iconText }}</span>
      <span>{{ messageText }}</span>
      <button
        v-if="connectionStatus === 'online' && pendingCount > 0"
        class="ml-2 rounded-md bg-white px-3 py-1 text-xs font-semibold shadow-sm transition-colors hover:bg-gray-50"
        @click="handleSync"
      >
        立即同步
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
