<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { shareApi } from "../api/client";
import type { Trip, Day, Activity } from "../types";
import { CATEGORY_LABELS, CATEGORY_COLORS } from "../types";
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";

const route = useRoute();
const code = route.params.code as string;

const trip = ref<Trip | null>(null);
const loading = ref(true);
const error = ref("");

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
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <h1 class="text-xl font-bold text-gray-900">✈️ TravelMate</h1>
        <span class="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700">🔗 分享行程</span>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-8">
      <div v-if="loading" class="py-20 text-center text-gray-400">載入中...</div>

      <div v-else-if="error" class="py-20 text-center">
        <p class="text-5xl mb-3">🔒</p>
        <p class="text-gray-500">{{ error }}</p>
      </div>

      <div v-else-if="trip" class="space-y-6">
        <!-- Trip info -->
        <div class="rounded-xl bg-white p-6 shadow-sm border border-gray-200">
          <h2 class="text-2xl font-bold text-gray-900">{{ trip.title }}</h2>
          <p v-if="trip.description" class="mt-2 text-gray-500">{{ trip.description }}</p>
          <p class="mt-2 text-sm text-gray-400">📅 {{ trip.start_date }} ~ {{ trip.end_date }}</p>
        </div>

        <p class="text-center text-sm text-gray-400">
          此為唯讀檢視，登入後可編輯自己的行程
        </p>
      </div>
    </main>
  </div>
</template>
