<script setup lang="ts">
import { ref, computed } from "vue";
import type { POI } from "../types";

interface RouteData {
  coordinates: [number, number][];
  distance: number;
  duration: number;
}

const props = defineProps<{
  tripId: string;
  pois: POI[];
}>();

const emit = defineEmits<{
  (e: "route", routeData: RouteData | null): void;
}>();

const selectedPoiIds = ref<Set<string>>(new Set());
const profile = ref<"driving" | "walking" | "cycling">("driving");
const loading = ref(false);
const routeData = ref<RouteData | null>(null);

const selectedPois = computed(() =>
  props.pois.filter((p) => selectedPoiIds.value.has(p.id))
);

const canPlan = computed(() => selectedPois.value.length >= 2);

function togglePoi(poiId: string) {
  const next = new Set(selectedPoiIds.value);
  if (next.has(poiId)) {
    next.delete(poiId);
  } else {
    next.add(poiId);
  }
  selectedPoiIds.value = next;
}

async function planRoute() {
  if (!canPlan.value) return;
  loading.value = true;
  routeData.value = null;

  const coords = selectedPois.value
    .filter((p) => p.lat != null && p.lng != null)
    .map((p) => `${p.lng},${p.lat}`)
    .join(";");

  try {
    const res = await fetch(
      `https://router.project-osrm.org/route/v1/${profile.value}/${coords}?overview=full&geometries=geojson`
    );
    if (!res.ok) {
      throw new Error(`OSRM 回傳錯誤: ${res.status}`);
    }
    const data = await res.json();
    if (data.code !== "Ok" || !data.routes?.length) {
      throw new Error("OSRM 無法規劃路線");
    }
    const route = data.routes[0];
    routeData.value = {
      coordinates: route.geometry.coordinates,
      distance: route.distance,
      duration: route.duration,
    };
    emit("route", routeData.value);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "路線規劃失敗";
    alert(msg);
  } finally {
    loading.value = false;
  }
}

function clearRoute() {
  routeData.value = null;
  selectedPoiIds.value = new Set();
  emit("route", null);
}
</script>

<template>
  <div class="rounded-xl border border-gray-200 bg-white shadow-sm">
    <div class="border-b border-gray-100 px-5 py-4">
      <h3 class="text-sm font-bold text-gray-900">📍 路線規劃</h3>
      <p class="mt-0.5 text-xs text-gray-400">勾選 2 個以上地點來規劃路線</p>
    </div>

    <!-- Profile Selector -->
    <div class="flex gap-2 px-5 py-3 border-b border-gray-100">
      <button
        v-for="(label, key) in { driving: '🚗 開車', walking: '🚶 步行', cycling: '🚴 單車' }"
        :key="key"
        @click="profile = key as any"
        :class="[
          'rounded-lg px-3 py-1.5 text-xs font-medium transition',
          profile === key ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
        ]"
      >
        {{ label }}
      </button>
    </div>

    <!-- POI Checkbox List -->
    <div class="max-h-64 overflow-y-auto divide-y divide-gray-50">
      <div
        v-for="poi in pois"
        :key="poi.id"
        class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition"
      >
        <input
          type="checkbox"
          :checked="selectedPoiIds.has(poi.id)"
          :disabled="poi.lat == null || poi.lng == null"
          @change="togglePoi(poi.id)"
          class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">
            {{ poi.name }}
          </p>
          <p class="text-xs text-gray-400 truncate">
            {{ poi.address || (poi.lat != null && poi.lng != null ? `${poi.lat?.toFixed(4)}, ${poi.lng?.toFixed(4)}` : '') }}
            <span v-if="poi.lat == null || poi.lng == null" class="text-red-400">(無座標)</span>
          </p>
        </div>
        <span
          v-if="poi.category"
          class="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600 flex-shrink-0"
        >
          {{ poi.category }}
        </span>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="pois.length === 0"
      class="px-5 py-8 text-center text-xs text-gray-300"
    >
      尚無景點，請先在 POI 頁面新增
    </div>

    <!-- Actions -->
    <div class="border-t border-gray-100 px-5 py-4 space-y-3">
      <!-- Route summary -->
      <div
        v-if="routeData"
        class="rounded-lg bg-indigo-50 px-4 py-3 text-sm"
      >
        <div class="flex items-center justify-between">
          <span class="text-gray-600">距離</span>
          <span class="font-semibold text-gray-900">
            {{ (routeData.distance / 1000).toFixed(1) }} km
          </span>
        </div>
        <div class="flex items-center justify-between mt-1">
          <span class="text-gray-600">預計時間</span>
          <span class="font-semibold text-gray-900">
            {{ Math.round(routeData.duration / 60) }} 分鐘
          </span>
        </div>
      </div>

      <div class="flex gap-2">
        <button
          @click="planRoute"
          :disabled="!canPlan || loading"
          class="flex-1 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50 transition-all flex items-center justify-center gap-2"
        >
          <span
            v-if="loading"
            class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
          ></span>
          {{ loading ? '規劃中...' : '🚗 規劃路線' }}
        </button>
        <button
          v-if="routeData"
          @click="clearRoute"
          class="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-all"
        >
          清除
        </button>
      </div>

      <p
        v-if="!canPlan && selectedPois.length > 0"
        class="text-xs text-amber-600 text-center"
      >
        請至少勾選 2 個有座標的景點
      </p>
    </div>
  </div>
</template>
