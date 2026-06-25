<script setup lang="ts">
import { onMounted, ref } from "vue";
import ToastContainer from "./components/ToastContainer.vue";
import { useAuthStore } from "./stores/auth";

const auth = useAuthStore();

const deferredPrompt = ref<any>(null);
const showInstallPrompt = ref(false);

onMounted(() => {
  auth.restoreSession();
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt.value = e;
    showInstallPrompt.value = true;
  });
});

async function handleInstall() {
  if (deferredPrompt.value) {
    deferredPrompt.value.prompt();
    const result = await deferredPrompt.value.userChoice;
    if (result.outcome === "accepted") {
      showInstallPrompt.value = false;
    }
    deferredPrompt.value = null;
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <ToastContainer />
    <router-view v-slot="{ Component, route: r }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="r.path" />
      </Transition>
    </router-view>

    <div
      v-if="showInstallPrompt"
      class="fixed bottom-20 left-4 right-4 z-50 max-w-sm mx-auto"
    >
      <div
        class="rounded-xl bg-white p-4 shadow-xl border border-gray-200 flex items-center gap-3"
      >
        <div>
          <p class="text-sm font-bold text-gray-900">安裝 TravelMate</p>
          <p class="text-xs text-gray-500">加到主畫面，隨時隨地使用</p>
        </div>
        <button
          @click="handleInstall"
          class="flex-shrink-0 rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
        >
          安裝
        </button>
        <button
          @click="showInstallPrompt = false"
          class="flex-shrink-0 text-gray-400 hover:text-gray-600 text-lg"
        >
          ✕
        </button>
      </div>
    </div>
  </div>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
