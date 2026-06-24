<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useTripStore } from "../stores/trip";
import api from "../api/client";
import OfflineBanner from "../components/OfflineBanner.vue";

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

// Pull-to-refresh
const pullDistance = ref(0);
const isRefreshing = ref(false);
const pullThreshold = 80;

let startY = 0;
let isPulling = false;

function onTouchStart(e: TouchEvent) {
  if (window.scrollY > 0) return;
  startY = e.touches[0].clientY;
  isPulling = true;
}

function onTouchMove(e: TouchEvent) {
  if (!isPulling || isRefreshing.value) return;
  const diff = e.touches[0].clientY - startY;
  if (diff > 0) {
    pullDistance.value = Math.min(diff * 0.5, 120);
  }
}

function onTouchEnd() {
  isPulling = false;
  if (pullDistance.value >= pullThreshold) {
    isRefreshing.value = true;
    pullDistance.value = 0;
    refreshData().finally(() => {
      isRefreshing.value = false;
    });
  } else {
    pullDistance.value = 0;
  }
}

async function refreshData() {
  await tripStore.fetchTrips();
}

async function handleDeleteTrip(tripId: string) {
  if (!confirm("確定刪除此行程？")) return;
  try {
    await tripStore.deleteTrip(tripId);
  } catch {
    // ignore
  }
}

async function handleCreate() {
  try {
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
  } catch {
    // ignore
  }
}

onMounted(() => {
  tripStore.fetchTrips();
});
</script>

<template>
  <div class="min-h-screen" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
    <!-- Pull-to-refresh indicator -->
    <div
      v-if="pullDistance > 0 || isRefreshing"
      class="flex items-center justify-center py-2 text-sm text-gray-500 transition-all"
      :style="{ transform: `translateY(${isRefreshing ? 0 : pullDistance}px)` }"
    >
      <span
        class="inline-block text-lg transition-transform duration-300"
        :class="pullDistance >= pullThreshold ? 'rotate-180' : ''"
      >↓</span>
      <span class="ml-2">
        {{ isRefreshing ? '載入中...' : pullDistance >= pullThreshold ? '釋放重新整理' : '下拉重新整理' }}
      </span>
    </div>
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

    <OfflineBanner />

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
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
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
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
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
                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
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
                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
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
                  list="countries"
                  placeholder="臺灣"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                />
              </div>
              <div class="flex-1">
                <label class="block text-xs text-gray-500">目的地國家</label>
                <input
                  v-model="newDest"
                  list="countries"
                  placeholder="日本"
                  @input="onDestChange(newDest)"
                  class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
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

      <!-- Loading -->      <!-- Country datalist -->
      <datalist id="countries">
        <option value="日本" /><option value="韓國" /><option value="台灣" /><option value="中國" /><option value="香港" />
        <option value="新加坡" /><option value="泰國" /><option value="越南" /><option value="印尼" /><option value="馬來西亞" />
        <option value="菲律賓" /><option value="柬埔寨" /><option value="緬甸" /><option value="印度" /><option value="尼泊爾" />
        <option value="英國" /><option value="法國" /><option value="德國" /><option value="義大利" /><option value="西班牙" />
        <option value="荷蘭" /><option value="瑞士" /><option value="奧地利" /><option value="捷克" /><option value="希臘" />
        <option value="葡萄牙" /><option value="土耳其" /><option value="冰島" /><option value="挪威" /><option value="瑞典" />
        <option value="美國" /><option value="加拿大" /><option value="墨西哥" /><option value="巴西" /><option value="阿根廷" />
        <option value="澳洲" /><option value="紐西蘭" /><option value="埃及" /><option value="摩洛哥" /><option value="南非" />
      </datalist>


      <div v-if="tripStore.trips.length === 0" class="flex items-center justify-center py-16">
        <div class="w-full max-w-md rounded-2xl border border-dashed border-gray-200 bg-white/50 px-8 py-12 text-center shadow-sm">
          <div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-indigo-50 text-5xl">🗺️</div>
          <h3 class="mb-2 text-xl font-bold text-gray-800">開始你的旅程</h3>
          <p class="mb-6 text-sm text-gray-500">還沒有任何行程，<br/>點擊下方按鈕建立你的第一個冒險吧！</p>
          <button
            @click="showCreate = true"
            class="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md hover:shadow-lg hover:from-indigo-500 hover:to-indigo-400 transition-all"
          >
            ＋ 建立新行程
          </button>
        </div>
      </div>

      <!-- Trip Cards -->
      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="trip in tripStore.trips"
          :key="trip.id"
          @click="router.push(`/trips/${trip.id}`)"
          class="cursor-pointer rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition"
        >
          <h3 class="text-lg font-bold text-gray-900">{{ trip.title }}</h3>
          <p v-if="trip.description" class="mt-1 text-sm text-gray-500 line-clamp-2">{{ trip.description }}</p>
          <div class="mt-3 flex items-center gap-2 text-xs text-gray-400">
            <span>📅 {{ trip.start_date }} ~ {{ trip.end_date }}</span>
          </div>
          <div class="mt-2 flex flex-wrap gap-1.5">
            <span v-if="trip.destination_country" class="inline-flex items-center gap-0.5 rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700">
              🌍 {{ trip.destination_country }}
            </span>
            <span v-if="trip.destination_tz_offset != null" class="inline-flex items-center gap-0.5 rounded bg-yellow-50 px-1.5 py-0.5 text-xs text-yellow-700">
              🕐 UTC{{ trip.destination_tz_offset >= 0 ? '+' : '' }}{{ trip.destination_tz_offset }}
            </span>
            <span v-if="trip.visibility === 'shared'" class="rounded bg-green-100 px-1.5 py-0.5 text-green-700">🔗 分享中</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
