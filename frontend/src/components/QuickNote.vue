<script setup lang="ts">
import { ref } from "vue";
import { memoryApi } from "../api/client";

const props = defineProps<{
  tripId: string;
  defaultDate?: string;
}>();

const emit = defineEmits<{
  saved: [];
}>();

const showInput = ref(false);
const noteText = ref("");
const saving = ref(false);

function open() {
  noteText.value = "";
  showInput.value = true;
  // Auto focus textarea after next tick
  setTimeout(() => {
    const textarea = document.querySelector<HTMLTextAreaElement>('.quick-note-input');
    textarea?.focus();
  }, 100);
}

async function save() {
  if (!noteText.value.trim()) return;
  saving.value = true;
  try {
    await memoryApi.create(props.tripId, {
      title: "📝 即時筆記",
      content: noteText.value.trim(),
      date: props.defaultDate || new Date().toISOString().split("T")[0],
    });
    noteText.value = "";
    showInput.value = false;
    emit("saved");
  } catch {
    // silent
  } finally {
    saving.value = false;
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    save();
  }
  if (e.key === "Escape") {
    showInput.value = false;
    noteText.value = "";
  }
}

defineExpose({ open });
</script>

<template>
  <div class="fixed bottom-28 md:bottom-24 right-4 z-40" v-if="!showInput">
    <button
      @click="open"
      class="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-indigo-600 to-indigo-500 text-white text-2xl shadow-xl hover:shadow-2xl hover:scale-105 transition-all"
      aria-label="新增即時筆記"
      title="快速筆記"
    >
      ✏️
    </button>
  </div>

  <Teleport to="body">
    <div v-if="showInput" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 p-4" @click.self="showInput = false">
      <div class="w-full max-w-md rounded-2xl bg-white p-5 shadow-2xl">
        <h3 class="text-sm font-bold text-gray-700 mb-2">📝 即時筆記</h3>
        <textarea
          v-model="noteText"
          class="quick-note-input w-full rounded-xl border border-gray-200 p-3 text-sm resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          rows="3"
          placeholder="寫下此刻的想法..."
          @keydown="onKeydown"
        ></textarea>
        <div class="flex justify-end gap-2 mt-3">
          <button @click="showInput = false" class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">取消</button>
          <button @click="save" :disabled="saving || !noteText.trim()"
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700 disabled:opacity-50">
            {{ saving ? '儲存中...' : '儲存 (Enter)' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
