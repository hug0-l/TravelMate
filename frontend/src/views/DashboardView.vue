<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useTripStore } from "../stores/trip";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import EmptyState from "../components/EmptyState.vue";

const router = useRouter();
const auth = useAuthStore();
const tripStore = useTripStore();

const showCreate = ref(false);
const newTitle = ref("");
const newStart = ref("");
const newDuration = ref(5);
const newEnd = ref("");
const newOrigin = ref("");
const newDest = ref("");
const newTzOffset = ref(0);
const useDuration = ref(true);

const countryTimezoneMap: Record<string, number> = {
  "日本": 9, "韓國": 9, "台灣": 8, "中國": 8, "香港": 8,
  "新加坡": 8, "泰國": 7, "越南": 7, "印尼": 7, "馬來西亞": 8,
  "印度": 5.5, "英國": 0, "法國": 1, "德國": 1, "義大利": 1,
  "西班牙": 1, "美國": -5, "加拿大": -5, "澳洲": 11, "紐西蘭": 13,
};

function onDestChange(newVal: string) {
  if (newVal in countryTimezoneMap) {
    newTzOffset.value = countryTimezoneMap[newVal];
  }
}

function onStartChange() {
  if (newStart.value && useDuration.value) {
    const start = new Date(newStart.value);
    const end = new Date(start);
    end.setDate(end.getDate() + newDuration.value - 1);
    newEnd.value = end.toISOString().split("T")[0];
  }
}

function onDurationChange() {
  onStartChange();
}

function resetForm() {
  newTitle.value = "";
  newStart.value = "";
  newDuration.value = 5;
  newEnd.value = "";
  newOrigin.value = "";
  newDest.value = "";
  newTzOffset.value = 0;
  useDuration.value = true;
  showCreate.value = false;
}

function closeModal() {
  showCreate.value = false;
}

async function handleCreate() {
  await tripStore.createTrip({
    title: newTitle.value,
    start_date: newStart.value,
    duration_days: useDuration.value ? newDuration.value : undefined,
    end_date: useDuration.value ? undefined : newEnd.value,
    origin_country: newOrigin.value || undefined,
    destination_country: newDest.value || undefined,
    destination_tz_offset: newDest.value ? newTzOffset.value : undefined,
  });
  resetForm();
}

onMounted(() => {
  tripStore.fetchTrips();
});
</script>

<template>
  <div class="min-h-screen">
    <!-- Nav -->
    <header class="bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <h1 class="text-xl font-bold text-white">✈️ TravelMate</h1>
        <div class="flex items-center gap-4">
          <span class="text-sm text-indigo-100">{{ auth.user?.name }}</span>
          <button
            @click="auth.logout(); router.push('/login')"
            class="text-sm text-indigo-200 hover:text-white transition-colors"
          >
            登出
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-8">
      <!-- Header -->
      <div class="mb-6 flex items-center justify-between">
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">
          <span class="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">我的旅程</span>
        </h2>
        <button
          @click="showCreate = true"
          class="rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md hover:shadow-lg hover:from-indigo-500 hover:to-indigo-400 transition-all"
        >
          ＋ 新行程
        </button>
      </div>

      <!-- Create Modal -->
      <div
        v-if="showCreate"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
        @click.self="closeModal"
      >
        <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
          <h3 class="mb-4 text-lg font-bold">建立新行程</h3>
          <form @submit.prevent="handleCreate" class="space-y-3">
            <input
              v-model="newTitle"
              placeholder="行程名稱（如：東京賞楓）"
              required
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
            />
            <div class="flex items-center gap-2">
              <label class="text-xs text-gray-500">計算方式：</label>
              <button
                type="button"
                @click="useDuration = true; onStartChange()"
                :class="['rounded px-3 py-1 text-xs font-medium transition', useDuration ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600']"
              >
                天數模式
              </button>
              <button
                type="button"
                @click="useDuration = false"
                :class="['rounded px-3 py-1 text-xs font-medium transition', !useDuration ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600']"
              >
                手動模式
              </button>
            </div>
            <div class="flex gap-2">
              <div class="flex-1">
                <label class="block text-xs text-gray-500">出發</label>
                <input
                  v-model="newStart"
                  type="date"
                  @change="onStartChange"
                  required
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                />
              </div>
              <template v-if="useDuration">
                <div class="flex-1">
                  <label class="block text-xs text-gray-500">天數</label>
                  <input
                    v-model.number="newDuration"
                    type="number"
                    min="1"
                    max="365"
                    @change="onDurationChange"
                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                  />
                </div>
              </template>
              <template v-else>
                <div class="flex-1">
                  <label class="block text-xs text-gray-500">結束</label>
                  <input
                    v-model="newEnd"
                    type="date"
                    required
                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                  />
                </div>
              </template>
            </div>
            <div v-if="useDuration && newStart && newDuration" class="rounded bg-blue-50 px-3 py-1.5 text-xs text-blue-600">
              預計結束：{{ newEnd }}
            </div>
            <div class="flex gap-2">
              <div class="flex-1">
                <label class="block text-xs text-gray-500">出發國家</label>
                <input
                  v-model="newOrigin"
                  placeholder="臺灣"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                />
              </div>
              <div class="flex-1">
                <label class="block text-xs text-gray-500">目的地國家</label>
                <input
                  v-model="newDest"
                  placeholder="日本"
                  @input="onDestChange(newDest)"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
                />
              </div>
            </div>
            <input v-model="newTzOffset" type="hidden" />
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" @click="closeModal" class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">
                取消
              </button>
              <button type="submit" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">
                建立
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Loading -->
      <EmptyState
        v-if="tripStore.trips.length === 0"
        icon="🗺️"
        title="開始你的旅程"
        description="還沒有任何行程，點擊下方按鈕建立你的第一個冒險吧！"
        actionText="＋ 建立新行程"
        @action="showCreate = true"
      />

      <!-- Trip Cards -->
      <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="trip in tripStore.trips"
          :key="trip.id"
          @click="router.push(`/trips/${trip.id}`)"
          class="group cursor-pointer overflow-hidden rounded-xl border border-gray-200 bg-white shadow-md hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200"
        >
          <!-- Gradient top strip -->
          <div class="h-1.5 bg-gradient-to-r from-indigo-500 to-indigo-400"></div>
          <div class="p-5">
            <h3 class="text-xl font-extrabold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ trip.title }}</h3>
            <p v-if="trip.description" class="mt-1.5 text-sm text-gray-500 line-clamp-2">{{ trip.description }}</p>
            <div class="mt-3 flex items-center gap-2 text-xs text-gray-400">
              <span>📅 {{ trip.start_date }} ~ {{ trip.end_date }}</span>
            </div>
            <div v-if="trip.start_date && trip.end_date" class="mt-2">
              <span class="inline-flex items-center gap-0.5 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-600">
                🕒 {{ String(Math.ceil((new Date(trip.end_date).getTime() - new Date(trip.start_date).getTime()) / 86400000) + 1) }} 天
              </span>
            </div>
            </div>
            <div class="mt-2 flex flex-wrap gap-1.5">
              <span v-if="trip.destination_country" class="inline-flex items-center gap-0.5 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
                🌍 {{ trip.destination_country }}
              </span>
              <span v-if="trip.destination_tz_offset != null" class="inline-flex items-center gap-0.5 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                🕐 UTC{{ trip.destination_tz_offset >= 0 ? '+' : '' }}{{ trip.destination_tz_offset }}
              </span>
              <span v-if="trip.visibility === 'shared'" class="inline-flex items-center gap-0.5 rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700">🔗 分享中</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
