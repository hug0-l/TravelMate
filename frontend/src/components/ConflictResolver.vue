<script setup lang="ts">
import type { ConflictEntry } from "../sync";

const props = defineProps<{
  conflicts: ConflictEntry[];
}>();

const emit = defineEmits<{
  (e: "resolve", conflict: ConflictEntry, choice: "local" | "server"): void;
}>();
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="w-full max-w-2xl rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b px-6 py-4">
            <h2 class="text-lg font-bold text-gray-800">衝突偵測</h2>
            <span class="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
              {{ conflicts.length }} 個衝突
            </span>
          </div>

          <div class="max-h-[70vh] space-y-4 overflow-y-auto px-6 py-4">
            <div
              v-for="(conflict, index) in conflicts"
              :key="conflict.change.id ?? index"
              class="rounded-xl border border-gray-200 bg-gray-50 p-4"
            >
              <div class="mb-3 flex items-center justify-between">
                <span class="text-sm font-semibold text-gray-700">
                  {{ conflict.change.action.toUpperCase() }} — {{ conflict.change.store }}
                </span>
                <span class="text-xs text-gray-400">{{ conflict.change.endpoint }}</span>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div
                  class="cursor-pointer rounded-lg border-2 p-3 transition-all"
                  :class="conflict.resolved === 'server'
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:border-indigo-300'"
                  @click="emit('resolve', conflict, 'server')"
                >
                  <div class="mb-1 flex items-center gap-1.5">
                    <input
                      type="radio"
                      :checked="conflict.resolved === 'server'"
                      class="h-4 w-4 accent-indigo-600"
                      @click.stop="emit('resolve', conflict, 'server')"
                    />
                    <span class="text-xs font-bold uppercase tracking-wide text-indigo-700">伺服器</span>
                  </div>
                  <pre class="mt-2 overflow-x-auto whitespace-pre-wrap break-words rounded bg-indigo-50/50 p-2 text-xs text-gray-600">{{ JSON.stringify(conflict.serverData, null, 2) }}</pre>
                </div>

                <div
                  class="cursor-pointer rounded-lg border-2 p-3 transition-all"
                  :class="conflict.resolved === 'local'
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:border-indigo-300'"
                  @click="emit('resolve', conflict, 'local')"
                >
                  <div class="mb-1 flex items-center gap-1.5">
                    <input
                      type="radio"
                      :checked="conflict.resolved === 'local'"
                      class="h-4 w-4 accent-indigo-600"
                      @click.stop="emit('resolve', conflict, 'local')"
                    />
                    <span class="text-xs font-bold uppercase tracking-wide text-indigo-700">本地</span>
                  </div>
                  <pre class="mt-2 overflow-x-auto whitespace-pre-wrap break-words rounded bg-indigo-50/50 p-2 text-xs text-gray-600">{{ JSON.stringify(conflict.localData, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 border-t px-6 py-4">
            <p class="text-xs text-gray-400">選擇要保留的版本</p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
