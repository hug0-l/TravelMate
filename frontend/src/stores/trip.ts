import { defineStore } from "pinia";
import { ref } from "vue";
import { tripApi, dayApi, activityApi } from "../api/client";
import type { Trip, Day, Activity } from "../types";
import { offlineDB } from "../db";
import { syncQueue } from "../sync";

async function _offlineSafeFetch<T>(
  apiCall: () => Promise<T>,
  cacheRead: () => Promise<T>,
  cacheWrite: (data: T) => Promise<void>
): Promise<T> {
  if (navigator.onLine) {
    const data = await apiCall();
    await cacheWrite(data);
    return data;
  }
  return cacheRead();
}

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
      if (navigator.onLine) {
        const [tripRes, daysRes] = await Promise.all([
          tripApi.get(tripId),
          dayApi.list(tripId),
        ]);
        currentTrip.value = tripRes.data;
        days.value = daysRes.data;
        await offlineDB.save("trips", tripRes.data);
        await Promise.all(daysRes.data.map((day: Day) => offlineDB.save("days", day)));
        await Promise.all(daysRes.data.map((day: Day) => fetchActivities(day.id)));
      } else {
        const trip = await offlineDB.get("trips", tripId);
        if (!trip) throw new Error("Trip not found offline");
        currentTrip.value = trip;
        const dayList = await offlineDB.getAllByIndex("days", "trip_id", tripId);
        days.value = dayList;
        await Promise.all(dayList.map((day: Day) => fetchActivities(day.id)));
      }
    } finally {
      loading.value = false;
    }
  }

  async function fetchDays(tripId: string) {
    await _offlineSafeFetch(
      async () => {
        const res = await dayApi.list(tripId);
        days.value = res.data;
        return res.data;
      },
      async () => {
        const data = await offlineDB.getAllByIndex("days", "trip_id", tripId);
        days.value = data;
        return data;
      },
      async (data: Day[]) => {
        await Promise.all(data.map((d) => offlineDB.save("days", d)));
      }
    );
  }

  async function fetchActivities(dayId: string) {
    await _offlineSafeFetch(
      async () => {
        const res = await activityApi.list(dayId);
        activities.value[dayId] = res.data;
        return res.data;
      },
      async () => {
        const data = await offlineDB.getAllByIndex("activities", "day_id", dayId);
        activities.value[dayId] = data;
        return data;
      },
      async (data: Activity[]) => {
        await Promise.all(data.map((a) => offlineDB.save("activities", a)));
      }
    );
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
    if (navigator.onLine) {
      const res = await tripApi.create(data);
      trips.value.unshift(res.data);
      await offlineDB.save("trips", res.data);
      return res.data;
    }
    const offlineTrip = { ...data, id: `offline_${Date.now()}` } as unknown as Trip;
    trips.value.unshift(offlineTrip);
    await offlineDB.save("trips", offlineTrip);
    await syncQueue.enqueue({
      store: "trips",
      action: "create",
      endpoint: "/api/trips/",
      method: "POST",
      body: data,
    });
    return offlineTrip;
  }

  async function deleteTrip(tripId: string) {
    if (navigator.onLine) {
      await tripApi.delete(tripId);
    } else {
      await offlineDB.delete("trips", tripId);
      await syncQueue.enqueue({
        store: "trips",
        action: "delete",
        endpoint: `/api/trips/${tripId}`,
        method: "DELETE",
      });
    }
    trips.value = trips.value.filter((t) => t.id !== tripId);
  }

  async function createDay(tripId: string, data: { date: string; title?: string }) {
    if (navigator.onLine) {
      const res = await dayApi.create(tripId, data);
      days.value.push(res.data);
      await offlineDB.save("days", res.data);
      return res.data;
    }
    const offlineDay = { ...data, id: `offline_${Date.now()}`, trip_id: tripId } as unknown as Day;
    days.value.push(offlineDay);
    await offlineDB.save("days", offlineDay);
    await syncQueue.enqueue({
      store: "days",
      action: "create",
      endpoint: `/api/trips/${tripId}/days`,
      method: "POST",
      body: data,
    });
    return offlineDay;
  }

  async function updateDay(dayId: string, data: Record<string, unknown>) {
    if (navigator.onLine) {
      const res = await dayApi.update(dayId, data);
      const idx = days.value.findIndex((d) => d.id === dayId);
      if (idx !== -1) days.value[idx] = res.data;
      await offlineDB.save("days", res.data);
    } else {
      const idx = days.value.findIndex((d) => d.id === dayId);
      if (idx !== -1) {
        days.value[idx] = { ...days.value[idx], ...data } as Day;
        await offlineDB.save("days", days.value[idx]);
      }
      await syncQueue.enqueue({
        store: "days",
        action: "update",
        endpoint: `/api/days/${dayId}`,
        method: "PUT",
        body: data,
      });
    }
  }

  async function deleteDay(dayId: string) {
    if (navigator.onLine) {
      try {
        await dayApi.delete(dayId);
      } catch {}
    } else {
      await offlineDB.delete("days", dayId);
      await syncQueue.enqueue({
        store: "days",
        action: "delete",
        endpoint: `/api/days/${dayId}`,
        method: "DELETE",
      });
    }
    days.value = days.value.filter((d) => d.id !== dayId);
    delete activities.value[dayId];
  }

  async function createActivity(dayId: string, data: { title: string; notes?: string; start_time?: string; end_time?: string; duration_minutes?: number; category?: string; location_id?: string; transport_mode?: string }) {
    if (navigator.onLine) {
      let res;
      try {
        res = await activityApi.create(dayId, data);
      } catch {}
      if (!res) return;
      if (!activities.value[dayId]) activities.value[dayId] = [];
      activities.value[dayId].push(res.data);
      await offlineDB.save("activities", res.data);
      return res.data;
    }
    const offlineAct = { ...data, id: `offline_${Date.now()}`, day_id: dayId } as unknown as Activity;
    if (!activities.value[dayId]) activities.value[dayId] = [];
    activities.value[dayId].push(offlineAct);
    await offlineDB.save("activities", offlineAct);
    await syncQueue.enqueue({
      store: "activities",
      action: "create",
      endpoint: `/api/days/${dayId}/activities`,
      method: "POST",
      body: data,
    });
    return offlineAct;
  }

  async function updateActivity(activityId: string, data: { title?: string; notes?: string; start_time?: string; end_time?: string; duration_minutes?: number; category?: string; location_id?: string; transport_mode?: string }) {
    if (navigator.onLine) {
      const res = await activityApi.update(activityId, data);
      for (const dayId in activities.value) {
        const idx = activities.value[dayId].findIndex((a) => a.id === activityId);
        if (idx !== -1) {
          activities.value[dayId][idx] = res.data;
          break;
        }
      }
      await offlineDB.save("activities", res.data);
    } else {
      for (const dayId in activities.value) {
        const idx = activities.value[dayId].findIndex((a) => a.id === activityId);
        if (idx !== -1) {
          activities.value[dayId][idx] = { ...activities.value[dayId][idx], ...data } as Activity;
          await offlineDB.save("activities", activities.value[dayId][idx]);
          break;
        }
      }
      await syncQueue.enqueue({
        store: "activities",
        action: "update",
        endpoint: `/api/activities/${activityId}`,
        method: "PUT",
        body: data,
      });
    }
  }

  async function deleteActivity(activityId: string) {
    if (navigator.onLine) {
      try {
        await activityApi.delete(activityId);
      } catch {}
    } else {
      await offlineDB.delete("activities", activityId);
      await syncQueue.enqueue({
        store: "activities",
        action: "delete",
        endpoint: `/api/activities/${activityId}`,
        method: "DELETE",
      });
    }
    for (const dayId in activities.value) {
      activities.value[dayId] = activities.value[dayId].filter(
        (a) => a.id !== activityId,
      );
    }
  }

  async function reorderDays(dayIds: string[]) {
    const oldDays = days.value.slice();
    days.value = days.value.slice().sort((a, b) => dayIds.indexOf(a.id) - dayIds.indexOf(b.id));
    if (navigator.onLine) {
      try {
        await dayApi.reorder(currentTrip.value!.id, dayIds);
      } catch {
        days.value = oldDays;
      }
    } else {
      await syncQueue.enqueue({
        store: "days",
        action: "update",
        endpoint: `/api/trips/${currentTrip.value!.id}/days/reorder`,
        method: "PUT",
        body: { day_ids: dayIds },
      });
    }
  }

  async function reorderActivities(dayId: string, activityIds: string[]) {
    const oldActs = (activities.value[dayId] || []).slice();
    activities.value[dayId] = (activities.value[dayId] || []).slice().sort((a, b) => activityIds.indexOf(a.id) - activityIds.indexOf(b.id));
    if (navigator.onLine) {
      try {
        await activityApi.reorder(dayId, activityIds);
      } catch {
        activities.value[dayId] = oldActs;
      }
    } else {
      await syncQueue.enqueue({
        store: "activities",
        action: "update",
        endpoint: `/api/days/${dayId}/activities/reorder`,
        method: "PUT",
        body: { activity_ids: activityIds },
      });
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
    fetchDays,
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
