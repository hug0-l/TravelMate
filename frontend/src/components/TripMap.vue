<script setup lang="ts">
import { LMap, LTileLayer, LMarker, LPopup, LPolyline, LIcon } from "@vue-leaflet/vue-leaflet";
import L from "leaflet";
import type { Activity, Day, POI } from "../types";
import { CATEGORY_LABELS } from "../types";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface ActivityMarker {
  lat: number;
  lng: number;
  activity: Activity;
  day: Day;
}

interface POIMarker {
  lat: number;
  lng: number;
  poi: POI;
}

const props = defineProps<{
  markers: ActivityMarker[];
  poiMarkers: POIMarker[];
  routeData: { coordinates: [number, number][]; distance: number; duration: number } | null;
  center: [number, number];
  zoom: number;
  height?: string;
}>();

const poiIcon = L.divIcon({ className: "poi-marker", html: "📍", iconSize: [24, 24] });
</script>

<template>
  <LMap :zoom="zoom" :center="center" :style="{ height: height || '100%', width: '100%' }">
    <LTileLayer
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      attribution="© OpenStreetMap contributors"
    />
    <LMarker v-for="(m, i) in markers" :key="'act-' + i" :lat-lng="[m.lat, m.lng]">
      <LPopup>
        <div class="text-sm">
          <p class="font-bold">{{ m.activity.title }}</p>
          <p class="text-xs text-gray-500">{{ m.day.date }} · {{ CATEGORY_LABELS[m.activity.category] }}</p>
        </div>
      </LPopup>
    </LMarker>
    <LMarker v-for="(pm, i) in poiMarkers" :key="'poi-' + i" :lat-lng="[pm.lat, pm.lng]">
      <LIcon :icon="poiIcon" />
      <LPopup>
        <div class="text-sm">
          <p class="font-bold">{{ pm.poi.name }}</p>
          <p class="text-xs text-gray-500">{{ pm.poi.category }}</p>
        </div>
      </LPopup>
    </LMarker>
    <LPolyline v-if="routeData" :lat-lngs="routeData.coordinates.map(c => [c[1], c[0]])" color="#4f46e5" :weight="4" />
  </LMap>
</template>