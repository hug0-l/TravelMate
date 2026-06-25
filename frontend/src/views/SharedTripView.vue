<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { shareApi } from "../api/client";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import type { Trip, Day, Activity } from "../types";
import { CATEGORY_LABELS, CATEGORY_COLORS } from "../types";
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import L from "leaflet";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const route = useRoute();
const code = route.params.code as string;

const trip = ref<Trip | null>(null);
const loading = ref(true);
const showMap = ref(false);
const error = ref("");

const mapMarkers = computed(() => {
  if (!trip.value?.days) return [];
  const markers: Array<{ lat: number; lng: number; title: string; date: string }> = [];
  for (const day of trip.value.days) {
    for (const act of day.activities || []) {
      if (act.location?.lat && act.location?.lng) {
        markers.push({
          lat: act.location.lat,
          lng: act.location.lng,
          title: act.title,
          date: day.date,
        });
      }
    }
  }
  return markers;
});

const mapCenter = computed<[number, number]>(() => {
  if (mapMarkers.value.length > 0) return [mapMarkers.value[0].lat, mapMarkers.value[0].lng] as [number, number];
  return [35.6762, 139.6503] as [number, number];
});

onMounted(async () => {
  try {
    const res = await shareApi.get(code);
    trip.value = res.data;
  } catch {
    error.value = "找不到此行程，或行程未開放分享";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <h1 class="text-xl font-bold text-white">✈️ TravelMate</h1>
        <span class="rounded bg-white/20 px-2.5 py-0.5 text-xs text-white">🔗 分享行程</span>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-8">
      <div v-if="loading" class="space-y-4">
        <SkeletonLoader :lines="2" hasAvatar />
        <SkeletonLoader :lines="4" hasImage />
        <SkeletonLoader :lines="3" />
      </div>

      <div v-else-if="error" class="py-20 text-center">
        <p class="text-5xl mb-3">🔒</p>
        <p class="text-gray-500">{{ error }}</p>
      </div>

      <div v-else-if="trip" class="space-y-6">
        <!-- Trip info -->
        <div class="rounded-xl bg-white p-6 shadow-sm border border-gray-200">
          <h2 class="text-2xl font-bold text-gray-900">{{ trip.title }}</h2>
          <p v-if="trip.description" class="mt-2 text-gray-500 whitespace-pre-wrap">{{ trip.description }}</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <span class="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-700">
              📅 {{ trip.start_date }} ~ {{ trip.end_date }}
            </span>
            <span v-if="trip.destination_country" class="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-700">
              🌍 {{ trip.destination_country }}
            </span>
          </div>
        </div>

        <!-- Map toggle -->
        <div v-if="mapMarkers.length > 0">
          <button
            @click="showMap = !showMap"
            class="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition flex items-center justify-center gap-2"
          >
            🗺️ {{ showMap ? '隱藏地圖' : '檢視地圖' }}
          </button>
          <div v-if="showMap" class="mt-2 h-[50vh] rounded-xl overflow-hidden border border-gray-200">
            <LMap :zoom="12" :center="mapCenter" style="height: 100%; width: 100%">
              <LTileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution="© OpenStreetMap contributors"
              />
              <LMarker v-for="(m, i) in mapMarkers" :key="i" :lat-lng="[m.lat, m.lng]">
                <LPopup>
                  <div class="text-sm">
                    <p class="font-bold">{{ m.title }}</p>
                    <p class="text-xs text-gray-500">{{ m.date }}</p>
                  </div>
                </LPopup>
              </LMarker>
            </LMap>
          </div>
        </div>

        <!-- Itinerary -->
        <div class="space-y-4">
          <h3 class="text-lg font-bold text-gray-900">📅 行程表</h3>
          <div v-for="day in trip.days || []" :key="day.id" class="rounded-xl bg-white p-5 shadow-sm border border-gray-200">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-sm font-bold text-gray-900">{{ day.date }}</span>
              <span v-if="day.title" class="text-sm text-gray-500">· {{ day.title }}</span>
            </div>
            <div v-if="!day.activities || day.activities.length === 0" class="text-xs text-gray-400 py-2">無活動</div>
            <div v-else class="space-y-2">
              <div v-for="act in day.activities" :key="act.id" class="flex items-start gap-3 rounded-lg bg-gray-50 px-3 py-2">
                <span class="w-12 flex-shrink-0 rounded bg-gray-200 px-1 py-0.5 text-center text-xs font-medium text-gray-600">
                  {{ act.start_time || '--:--' }}
                </span>
                <span class="flex-1 text-sm text-gray-800">{{ act.title }}</span>
                <span v-if="act.notes" class="text-xs text-gray-400 truncate max-w-[120px]">{{ act.notes }}</span>
              </div>
            </div>
          </div>
        </div>

        <p class="text-center text-sm text-gray-400 pt-4">
          此為唯讀檢視，登入後可編輯自己的行程
        </p>
      </div>
    </main>
  </div>
</template>