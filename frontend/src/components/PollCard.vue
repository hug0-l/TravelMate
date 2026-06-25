<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import api from "../api/client";
import { useToast } from "../composables/useToast";

const props = defineProps<{
  tripId: string;
}>();

const { add } = useToast();

interface PollOption {
  id: string;
  label: string;
  vote_count: number;
  voted: boolean;
}

interface Poll {
  id: string;
  trip_id: string;
  creator_id: string;
  creator_name: string;
  question: string;
  is_closed: boolean;
  options: PollOption[];
  total_votes: number;
  created_at: string | null;
}

const polls = ref<Poll[]>([]);
const loading = ref(false);
const showCreate = ref(false);
const newQuestion = ref("");
const newOptions = ref<string[]>(["", ""]);

async function fetchPolls() {
  loading.value = true;
  try {
    const res = await api.get(`/trips/${props.tripId}/polls`);
    polls.value = res.data;
  } catch {
    polls.value = [];
  } finally {
    loading.value = false;
  }
}

async function handleVote(pollId: string, optionId: string) {
  try {
    await api.post(`/polls/${pollId}/vote`, { option_id: optionId });
    await fetchPolls();
  } catch {
    add("error", "投票失敗");
  }
}

function addOption() {
  if (newOptions.value.length < 10) {
    newOptions.value.push("");
  }
}

function removeOption(i: number) {
  if (newOptions.value.length > 2) {
    newOptions.value.splice(i, 1);
  }
}

async function handleCreate() {
  if (!newQuestion.value.trim()) return;
  const options = newOptions.value.map(o => o.trim()).filter(Boolean);
  if (options.length < 2) {
    add("error", "至少需要 2 個選項");
    return;
  }
  try {
    await api.post(`/trips/${props.tripId}/polls`, {
      question: newQuestion.value.trim(),
      options,
    });
    showCreate.value = false;
    newQuestion.value = "";
    newOptions.value = ["", ""];
    await fetchPolls();
    add("success", "投票已建立");
  } catch {
    add("error", "建立投票失敗");
  }
}

function getPercentage(option: PollOption, total: number): number {
  if (total === 0) return 0;
  return Math.round((option.vote_count / total) * 100);
}

async function handleClosePoll(pollId: string) {
  try {
    await api.post(`/polls/${pollId}/close`);
    await fetchPolls();
    add("success", "投票已截止");
  } catch {
    add("error", "截止投票失敗");
  }
}

function getMaxVoteCount(): number {
  return Math.max(...polls.value.flatMap(p => p.options.map(o => o.vote_count)), 0);
}

onMounted(fetchPolls);
</script>

<template>
  <div>
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-900">📊 投票</h2>
      <button @click="showCreate = true" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">＋ 新投票</button>
    </div>

    <div v-if="loading" class="py-12 text-center text-gray-400 animate-pulse">載入中...</div>

    <div v-else-if="polls.length === 0" class="py-16 text-center">
      <p class="text-5xl mb-3">📊</p>
      <p class="text-sm text-gray-400">還沒有投票，按「＋ 新投票」開始</p>
    </div>

    <div v-else class="space-y-4">
      <div v-for="poll in polls" :key="poll.id" class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-bold text-gray-900">{{ poll.question }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ poll.creator_name }} · {{ poll.total_votes }} 票{{ poll.is_closed ? ' · 🔒 已截止' : '' }}</p>
          </div>
          <button
            v-if="!poll.is_closed"
            @click.stop="handleClosePoll(poll.id)"
            class="text-xs text-gray-400 hover:text-red-500 ml-2 flex-shrink-0"
            title="截止投票"
          >
            🔒 截止
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="option in poll.options" :key="option.id"
            class="relative overflow-hidden rounded-lg border transition cursor-pointer"
            :class="[
              option.voted ? 'border-indigo-400 bg-indigo-50' : 'border-gray-200 hover:border-indigo-200',
              poll.is_closed ? 'cursor-default' : 'cursor-pointer',
            ]"
            @click="!poll.is_closed && handleVote(poll.id, option.id)"
          >
            <div class="absolute left-0 top-0 h-full bg-indigo-100 transition-all duration-500"
              :style="{ width: getPercentage(option, poll.total_votes) + '%' }">
            </div>
            <div class="relative flex items-center justify-between px-4 py-3">
              <div class="flex items-center gap-2">
                <span v-if="option.voted" class="text-indigo-600 text-sm">✓</span>
                <span class="text-sm font-medium text-gray-800">{{ option.label }}</span>
              </div>
              <span class="text-xs font-semibold text-gray-500">
                {{ option.vote_count }} 票 ({{ getPercentage(option, poll.total_votes) }}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showCreate = false">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">📊 新增投票</h3>
        <form @submit.prevent="handleCreate" class="space-y-3">
          <input v-model="newQuestion" placeholder="問題（如：晚餐吃什麼？）" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
          <div class="space-y-2">
            <label class="block text-xs text-gray-500">選項</label>
            <div v-for="(opt, i) in newOptions" :key="i" class="flex gap-2">
              <input v-model="newOptions[i]" :placeholder="`選項 ${i + 1}`" class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm" />
              <button v-if="newOptions.length > 2" type="button" @click="removeOption(i)" class="text-gray-300 hover:text-red-500">✕</button>
            </div>
            <button v-if="newOptions.length < 10" type="button" @click="addOption" class="text-xs text-indigo-600 hover:underline">＋ 新增選項</button>
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showCreate = false" class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">取消</button>
            <button type="submit" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">建立投票</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
