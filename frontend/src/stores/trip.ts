import { defineStore } from "pinia";
import { ref } from "vue";
import { tripApi, dayApi, activityApi } from "../api/client";
import type { Trip, Day, Activity } from "../types";

export const useTripStore = defineStore("trip", () => {
  const trips = ref<Trip[]>([]);
  const currentTrip = ref<Trip | null>(null);
  const days = ref<Day[]>([]);
  const activities = ref<Record<string, Activity[]>>({});
  const loading = ref(false);

  async function fetchTrips() {
    try {
      const res = await tripApi.list();
      trips.value = res.data;
    } catch {
      trips.value = [];
    }
  }

  async function fetchTrip(tripId: string) {
    loading.value = true;
    try {
      const [tripRes, daysRes] = await Promise.all([
        tripApi.get(tripId),
        dayApi.list(tripId),
      ]);
      currentTrip.value = tripRes.data;
      days.value = daysRes.data;
      // Fetch activities in parallel
      await Promise.all(daysRes.data.map((day: { id: string }) => fetchActivities(day.id)));
    } finally {
      loading.value = false;
    }
  }

  async function fetchActivities(dayId: string) {
    const res = await activityApi.list(dayId);
    activities.value[dayId] = res.data;
  }

  async function createTrip(data: {
    title: string;
    start_date: string;
    end_date?: string;
    duration_days?: number;
    origin_country?: string;
    destination_country?: string;
    destination_tz_offset?: number;
  }) {
    const res = await tripApi.create(data);
    trips.value.unshift(res.data);
    return res.data;
  }

  async function deleteTrip(tripId: string) {
    await tripApi.delete(tripId);
    trips.value = trips.value.filter((t) => t.id !== tripId);
  }

  async function createDay(tripId: string, data: { date: string; title?: string }) {
    const res = await dayApi.create(tripId, data);
    days.value.push(res.data);
    return res.data;
  }

  async function updateDay(dayId: string, data: Record<string, unknown>) {
    const res = await dayApi.update(dayId, data);
    const idx = days.value.findIndex((d) => d.id === dayId);
    if (idx !== -1) days.value[idx] = res.data;
  }

  async function deleteDay(dayId: string) {
    try {
      await dayApi.delete(dayId);
    } catch {}
    days.value = days.value.filter((d) => d.id !== dayId);
    delete activities.value[dayId];
  }

  async function createActivity(dayId: string, data: { title: string; notes?: string; start_time?: string; duration_minutes?: number; category?: string; location_id?: string }) {
    let res;
    try {
      res = await activityApi.create(dayId, data);
    } catch {}
    if (!res) return;
    if (!activities.value[dayId]) activities.value[dayId] = [];
    activities.value[dayId].push(res.data);
    return res.data;
  }

  async function updateActivity(activityId: string, data: { title?: string; notes?: string; start_time?: string; duration_minutes?: number; category?: string; location_id?: string }) {
    const res = await activityApi.update(activityId, data);
    for (const dayId in activities.value) {
      const idx = activities.value[dayId].findIndex((a) => a.id === activityId);
      if (idx !== -1) {
        activities.value[dayId][idx] = res.data;
        break;
      }
    }
  }

  async function deleteActivity(activityId: string) {
    try {
      await activityApi.delete(activityId);
    } catch {}
    for (const dayId in activities.value) {
      activities.value[dayId] = activities.value[dayId].filter(
        (a) => a.id !== activityId,
      );
    }
  }

  async function reorderDays(dayIds: string[]) {
    const oldDays = days.value.slice();
    days.value = days.value.slice().sort((a, b) => dayIds.indexOf(a.id) - dayIds.indexOf(b.id));
    try {
      await dayApi.reorder(currentTrip.value!.id, dayIds);
    } catch {
      days.value = oldDays;
    }
  }

  async function reorderActivities(dayId: string, activityIds: string[]) {
    const oldActs = (activities.value[dayId] || []).slice();
    activities.value[dayId] = (activities.value[dayId] || []).slice().sort((a, b) => activityIds.indexOf(a.id) - activityIds.indexOf(b.id));
    try {
      await activityApi.reorder(dayId, activityIds);
    } catch {
      activities.value[dayId] = oldActs;
    }
  }

  return {
    trips,
    currentTrip,
    days,
    activities,
    loading,
    fetchTrips,
    fetchTrip,
    createTrip,
    deleteTrip,
    createDay,
    updateDay,
    deleteDay,
    createActivity,
    updateActivity,
    deleteActivity,
    reorderDays,
    reorderActivities,
  };
});
