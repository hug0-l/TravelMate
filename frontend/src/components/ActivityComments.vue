<script setup lang="ts">
import { ref, computed } from "vue";
import { commentApi } from "../api/client";
import { useToast } from "../composables/useToast";
import { useAuthStore } from "../stores/auth";
import type { ActivityComment } from "../types";

const props = defineProps<{
  activityId: string;
}>();

const auth = useAuthStore();
const { add: toast } = useToast();

const expanded = ref(false);
const loaded = ref(false);
const loading = ref(false);
const comments = ref<ActivityComment[]>([]);
const newContent = ref("");
const submitting = ref(false);

function relativeTime(iso: string | null): string {
  if (!iso) return "";
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return "剛剛";
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}分鐘前`;
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour}小時前`;
  const diffDay = Math.floor(diffHour / 24);
  if (diffDay < 7) return `${diffDay}天前`;
  const d = new Date(iso);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const h = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${y}-${m}-${day} ${h}:${min}`;
}

const sortedComments = computed(() => {
  return [...comments.value].sort(
    (a, b) => new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime(),
  );
});

async function fetchComments() {
  loading.value = true;
  try {
    const res = await commentApi.list(props.activityId);
    comments.value = res.data as ActivityComment[];
    loaded.value = true;
  } catch {
    toast("error", "無法載入留言");
  } finally {
    loading.value = false;
  }
}

async function toggle() {
  expanded.value = !expanded.value;
  if (expanded.value && !loaded.value) {
    await fetchComments();
  }
}

async function submitComment() {
  const content = newContent.value.trim();
  if (!content || submitting.value) return;
  submitting.value = true;
  try {
    const res = await commentApi.create(props.activityId, { content });
    comments.value.push(res.data as ActivityComment);
    newContent.value = "";
    toast("success", "留言已新增");
  } catch {
    toast("error", "留言失敗");
  } finally {
    submitting.value = false;
  }
}

async function deleteComment(commentId: string) {
  try {
    await commentApi.delete(commentId);
    comments.value = comments.value.filter((c) => c.id !== commentId);
    toast("success", "留言已刪除");
  } catch {
    toast("error", "刪除留言失敗");
  }
}
</script>

<template>
  <div>
    <button
      @click="toggle"
      class="text-xs text-gray-400 hover:text-indigo-600 transition"
    >
      💬 留言 ({{ comments.length }})
    </button>

    <div v-if="expanded" class="rounded-xl border border-gray-200 bg-gray-50 p-3 mt-2 space-y-2">
      <!-- Loading -->
      <template v-if="loading">
        <div class="text-xs text-gray-400 text-center py-2">
          載入中...
        </div>
      </template>

      <!-- Empty -->
      <template v-else-if="sortedComments.length === 0">
        <div class="text-xs text-gray-400 text-center py-2">
          尚無留言，來寫下第一則留言吧！
        </div>
      </template>

      <!-- Comment list -->
      <template v-else>
        <div v-for="comment in sortedComments" :key="comment.id" class="flex gap-2 items-start">
          <div class="h-6 w-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
            {{ comment.user_name.charAt(0) }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-700">{{ comment.user_name }}</span>
              <span class="text-[10px] text-gray-400">{{ relativeTime(comment.created_at) }}</span>
            </div>
            <p class="text-sm text-gray-600 whitespace-pre-wrap break-words">{{ comment.content }}</p>
          </div>
          <button
            v-if="comment.user_id === auth.user?.id"
            @click="deleteComment(comment.id)"
            class="text-xs text-gray-400 hover:text-red-500 transition flex-shrink-0 mt-0.5"
            title="刪除留言"
          >
            ✕
          </button>
        </div>
      </template>

      <!-- Add comment -->
      <div class="flex gap-2 items-start pt-1">
        <textarea
          v-model="newContent"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 resize-none"
          rows="2"
          placeholder="寫下留言..."
        ></textarea>
        <button
          @click="submitComment"
          :disabled="submitting || !newContent.trim()"
          class="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs text-white hover:bg-indigo-700 disabled:opacity-50 flex-shrink-0"
        >
          {{ submitting ? "送出中..." : "送出" }}
        </button>
      </div>
    </div>
  </div>
</template>
