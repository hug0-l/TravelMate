<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useTripStore } from "../stores/trip";
import { useAuthStore } from "../stores/auth";
import { geocodeApi, memoryApi } from "../api/client";
import api from "../api/client";
import { trimmed, trimmedOrUndefined } from "../utils/trim";
import type { Memory } from "../types";
import {
  CATEGORY_LABELS,
  CATEGORY_COLORS,
  type Activity,
  type ActivityCategory,
  type GeocodeResult,
  type Day,
} from "../types";
import TripMap from "../components/TripMap.vue";
import { useTripSocket } from "../stores/ws";

import SkeletonLoader from "../components/SkeletonLoader.vue";
import EmptyState from "../components/EmptyState.vue";
import ErrorState from "../components/ErrorState.vue";
import ConfirmModal from "../components/ConfirmModal.vue";
import { VueDraggable } from 'vue-draggable-plus';
import POIManager from "../components/POIManager.vue";
import RoutePlanner from "../components/RoutePlanner.vue";
import { poiApi } from "../api/client";
import type { POI } from "../types";
import OfflineBanner from "../components/OfflineBanner.vue";
import { usePullToRefresh } from "../hooks/usePullToRefresh";
import { useToast } from "../composables/useToast";
import { usePhotoUpload } from "../composables/usePhotoUpload";
import { useSwipeTabs } from "../composables/useSwipe";
import { useDarkMode } from "../composables/useDarkMode";
import { useTripBudget } from "../composables/useTripBudget";
import { useTripMembers } from "../composables/useTripMembers";
import { useTripMemories } from "../composables/useTripMemories";
import QuickNote from "../components/QuickNote.vue";
import PackingList from "../components/PackingList.vue";
import PollCard from "../components/PollCard.vue";
const route = useRoute();
const router = useRouter();
const tripStore = useTripStore();
const auth = useAuthStore();
const navigatorObj = window.navigator;
const quickNoteRef = ref<InstanceType<typeof QuickNote> | null>(null);
const { add: addToast } = useToast();

let tripId = route.params.id as string;

// Tabs
const activeTab = ref<"itinerary" | "map" | "budget" | "memories" | "poi" | "packing" | "photos" | "polls">("itinerary");
// POI state
const pois = ref<POI[]>([]);
const poisLoading = ref(false);
const routeData = ref<{ coordinates: [number, number][]; distance: number; duration: number } | null>(null);

async function fetchPois() {
  poisLoading.value = true;
  try {
    const res = await poiApi.list(tripId);
    pois.value = res.data;
  } catch {
    pois.value = [];
  } finally {
    poisLoading.value = false;
  }
}

function onRoute(data: { coordinates: [number, number][]; distance: number; duration: number } | null) {
  routeData.value = data;
}

// Pull-to-refresh
const { onTouchStart: onSwipeStart, onTouchEnd: onSwipeEnd } = useSwipeTabs(activeTab);
const { isDark, toggle: toggleDark } = useDarkMode();
const { pullDistance, isRefreshing, pullThreshold, onTouchStart, onTouchMove, onTouchEnd } = usePullToRefresh(async () => {
  await tripStore.fetchTrip(tripId);
  membersCtx.fetchMembers();
  budget.fetchBudget();
  fetchBudgetExpenses();
  memoriesCtx.fetchMemories();
  fetchPois();
});

// WebSocket
const socket = useTripSocket(tripId);

watch(() => route.params.id, (newId) => {
  if (newId && newId !== tripId) {
    tripId = newId as string;
    tripStore.fetchTrip(tripId as string);
    socket.disconnect();
    socket.connect();
    membersCtx.fetchMembers();
    budget.fetchBudget();
    fetchBudgetExpenses();
    memoriesCtx.fetchMemories();
    fetchPois();
  }
});

const membersCtx = useTripMembers(tripId);
const budget = useTripBudget(tripId);
const memoriesCtx = useTripMemories(tripId);

// Destructure budget for template
const {
  budgetData, budgetLoading, expenses, expensesLoading,
  showAddExpense, showSettleUp, settleUpData, settleLoading,
  newExpenseTitle, newExpenseAmount, newExpenseCategory, newExpensePaidBy, newExpenseSplitWith, creatingExpense,
  fetchExpenses: fetchBudgetExpenses, handleDeleteExpense,
  openAddExpense, handleAddExpense,
  fetchSettleUp, copySettleUp,
} = budget;

// Destructure members for template
const {
  showMemberModal, members, membersLoading,
  inviteEmail, inviteMsg, handleInvite,
} = membersCtx;

// Destructure memories for template
const {
  memories, memoriesLoading, showAddMemory,
  newMemTitle, newMemContent, newMemDate,
  newMemPhotos, handleFileSelect, removePhoto,
  allTripPhotos,
  handleAddMemory, handleDeleteMemory,
} = memoriesCtx;





// New day modal
const showNewDay = ref(false);
const newDayDate = ref("");
const newDayTitle = ref("");

// New activity modal
const showNewActivity = ref(false);
const activeDayId = ref("");
const newActTitle = ref("");
const newActCategory = ref<ActivityCategory>("other");
const newActTime = ref("");
const newActEndTime = ref("");
const newActTransportMode = ref("");
const newActAssignee = ref("");
const newActNotes = ref("");
// Edit activity modal
const showEditActivity = ref(false);
const editingActId = ref("");
const editActDayId = ref("");
const editActTitle = ref("");
const editActCategory = ref<ActivityCategory>("other");
const editActStartTime = ref("");
const editActEndTime = ref("");
const editActNotes = ref("");
const editActTransportMode = ref("");
const editActAssignee = ref("");

function openEditActivity(act: Activity) {
  editingActId.value = act.id;
  editActDayId.value = act.day_id;
  editActTitle.value = act.title;
  editActCategory.value = act.category;
  editActStartTime.value = act.start_time || "";
  editActEndTime.value = act.end_time || "";
  editActNotes.value = act.notes || "";
  editActTransportMode.value = act.transport_mode || "";
  editActAssignee.value = (act as any).assignee_id || "";
  showEditActivity.value = true;
}

async function handleUpdateActivity() {
  if (!editingActId.value) return;
  try {
    await tripStore.updateActivity(editingActId.value, {
      title: editActTitle.value,
      category: editActCategory.value,
      start_time: editActStartTime.value || undefined,
      end_time: editActEndTime.value || undefined,
      notes: editActNotes.value || undefined,
      transport_mode: editActTransportMode.value || undefined,
      assignee_id: editActAssignee.value || undefined,
    });
    showEditActivity.value = false;
    addToast("success", "活動已更新");
  } catch {
    addToast("error", "更新活動失敗");
  }
}

// Geocode search
const geoQuery = ref("");
const geoResults = ref<GeocodeResult[]>([]);
const showGeoResults = ref(false);

// Share
const showShareModal = ref(false);
const baseUrl = window.location.origin;
const shareUrl = computed(() => `${baseUrl}/share/${tripStore.currentTrip?.share_code}`);
const inviteUrl = computed(() => `${baseUrl}/join?trip=${tripStore.currentTrip?.id}&code=${tripStore.currentTrip?.join_code}`);

function openNewActivity(dayId: string) {
  activeDayId.value = dayId;
  newActTitle.value = "";
  newActCategory.value = "other";
  newActTime.value = "";
  newActEndTime.value = "";
  newActNotes.value = "";
  newActTransportMode.value = "";
  newActAssignee.value = "";
  showNewActivity.value = true;
}

const creatingDay = ref(false);

async function handleCreateDay() {
  if (creatingDay.value) return;
  creatingDay.value = true;
  try {
    await tripStore.createDay(tripId, {
      date: newDayDate.value,
      title: trimmedOrUndefined(newDayTitle.value),
    });
    showNewDay.value = false;
    newDayDate.value = "";
    newDayTitle.value = "";
  } catch {
    addToast("error", "新增天數失敗");
  } finally {
    creatingDay.value = false;
  }
}

const creatingActivity = ref(false);

async function handleCreateActivity() {
  if (creatingActivity.value) return;
  creatingActivity.value = true;
  try {
    await tripStore.createActivity(activeDayId.value, {
      title: trimmed(newActTitle.value),
      category: newActCategory.value,
      start_time: newActTime.value || undefined,
      end_time: newActEndTime.value || undefined,
      notes: newActNotes.value || undefined,
      transport_mode: newActTransportMode.value || undefined,
      assignee_id: newActAssignee.value || undefined,
    });
    showNewActivity.value = false;
    addToast("success", "活動已新增");
  } catch {
    addToast("error", "新增活動失敗");
  } finally {
    creatingActivity.value = false;
  }
}

// Delete confirmation
const showDeleteConfirm = ref(false);
const deletingActivityId = ref("");
const deletingDayId = ref("");

function confirmDeleteActivity(activityId: string) {
  deletingActivityId.value = activityId;
  deletingDayId.value = "";
  showDeleteConfirm.value = true;
}

function confirmDeleteDay(dayId: string) {
  deletingDayId.value = dayId;
  deletingActivityId.value = "";
  showDeleteConfirm.value = true;
}

async function handleDeleteConfirm() {
  try {
    if (deletingActivityId.value) {
      await tripStore.deleteActivity(deletingActivityId.value);
    } else if (deletingDayId.value) {
      await tripStore.deleteDay(deletingDayId.value);
    }
  } catch {
    addToast("error", "刪除失敗");
  } finally {
    showDeleteConfirm.value = false;
    deletingActivityId.value = "";
    deletingDayId.value = "";
  }
}

function copyShareUrl() {
  const url = shareUrl.value;
  if (url && navigatorObj.clipboard) {
    navigatorObj.clipboard.writeText(url);
  }
}
function copyInviteLink() {
  const url = inviteUrl.value;
  if (url && navigatorObj.clipboard) {
    navigatorObj.clipboard.writeText(url);
  }
}
function exportItinerary() {
  const trip = tripStore.currentTrip;
  if (!trip) return;
  
  let text = `# ${trip.title}\n`;
  text += `📅 ${trip.start_date} ~ ${trip.end_date}\n`;
  if (trip.destination_country) text += `🌍 ${trip.destination_country}\n`;
  text += `\n`;
  
  for (const day of tripStore.days) {
    text += `## ${day.date}${day.title ? ' - ' + day.title : ''}\n`;
    const acts = tripStore.activities[day.id] || [];
    for (const act of acts) {
      const time = act.start_time || '--:--';
      text += `- [${time}] ${act.title}`;
      if (act.notes) text += ` — ${act.notes}`;
      text += `\n`;
    }
    if (acts.length === 0) text += `- (無活動)\n`;
    text += `\n`;
  }
  
  // Copy to clipboard
  if (navigatorObj.clipboard) {
    navigatorObj.clipboard.writeText(text);
  }
}

async function handleToggleShare() {
  const trip = tripStore.currentTrip;
  if (!trip) return;
  try {
    const newVis = trip.visibility === "shared" ? "private" : "shared";
    await api.put(`/trips/${tripId}`, { visibility: newVis });
    trip.visibility = newVis as "shared" | "private";
    addToast("success", newVis === "shared" ? "行程已公開分享" : "行程已設為私人");
  } catch {
    addToast("error", "切換分享狀態失敗");
  }
}

// Geocode search
let geoTimeout: ReturnType<typeof setTimeout>;
function onGeoInput() {
  clearTimeout(geoTimeout);
  if (geoQuery.value.length < 2) {
    geoResults.value = [];
    return;
  }
  geoTimeout = setTimeout(async () => {
    try {
      const res = await geocodeApi.search(geoQuery.value);
      geoResults.value = res.data;
      showGeoResults.value = true;
    } catch {
      geoResults.value = [];
    }
  }, 400);
}

function selectGeoResult(result: GeocodeResult) {
  geoQuery.value = result.display_name;
  showGeoResults.value = false;
}

// Map center — use first activity with real coordinates, fallback to Tokyo
const mapCenter = computed<[number, number]>(() => {
  for (const day of tripStore.days) {
    const acts = tripStore.activities[day.id] || [];
    for (const act of acts) {
      if (act.location?.lat && act.location?.lng) return [act.location.lat, act.location.lng] as [number, number];
    }
  }
  return [35.6762, 139.6503] as [number, number];
});

const mapZoom = ref(12);

const mapMarkers = computed(() => {
  const markers: Array<{ lat: number; lng: number; activity: Activity; day: Day }> = [];
  for (const day of tripStore.days) {
    const acts = tripStore.activities[day.id] || [];
    for (const act of acts) {
      if (act.location?.lat && act.location?.lng) {
        markers.push({
          lat: act.location.lat,
          lng: act.location.lng,
          activity: act,
          day,
        });
      }
    }
  }
  return markers;
});

const poiMarkers = computed(() => {
  return pois.value
    .filter(p => p.lat && p.lng)
    .map(p => ({
      lat: p.lat!,
      lng: p.lng!,
      poi: p,
    }));
});

const todaySummary = computed(() => {
  const trip = tripStore.currentTrip;
  if (!trip || !trip.start_date || !trip.end_date) return null;
  const today = new Date().toISOString().split("T")[0];
  if (today < trip.start_date || today > trip.end_date) return null;
  
  // Find today's day
  const todayDay = tripStore.days.find(d => d.date === today);
  if (!todayDay) return null;
  
  const todayActs = tripStore.activities[todayDay.id] || [];
  const todayExpenses = expenses.value.filter(e => {
    // Approximate: check if expense date matches today (if expense model has date)
    return true; // simplified - just show count
  });
  
  return {
    date: today,
    dayTitle: todayDay.title,
    activityCount: todayActs.length,
    completedCount: todayActs.filter(a => a.start_time && a.start_time < new Date().toTimeString().slice(0, 5)).length,
  };
});
const tripStats = computed(() => {
  const trip = tripStore.currentTrip;
  if (!trip) return null;

  // Count all activities
  let totalActivities = 0;
  const allLocations = new Set<string>();
  for (const day of tripStore.days) {
    const acts = tripStore.activities[day.id] || [];
    totalActivities += acts.length;
    for (const act of acts) {
      if (act.location?.name) allLocations.add(act.location.name);
    }
  }

  // Total expenses from budget data
  const totalExpenses = budgetData.value?.total_expenses || 0;

  // Total memories with photos
  const photosCount = memories.value.reduce((sum, m) => sum + (m.photo_urls?.length || 0), 0);

  // Trip duration
  const durationDays = tripStore.days.length;

  return {
    durationDays,
    totalActivities,
    locations: allLocations.size,
    totalExpenses,
    photosCount,
  };
});

const BUDGET_LABELS: Record<string, string> = {
  food: "🍜 美食",
  transport: "🚆 交通",
  accommodation: "🏨 住宿",
  attraction: "🏛️ 景點",
  shopping: "🛍️ 購物",
  other: "📌 其他",
};



function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") {
    showNewDay.value = false;
    showNewActivity.value = false;
    showEditActivity.value = false;
    showAddMemory.value = false;
    showMemberModal.value = false;
    showShareModal.value = false;
    showAddExpense.value = false;
    showSettleUp.value = false;
    showDeleteConfirm.value = false;
  }
}

onMounted(async () => {
  try {
    await tripStore.fetchTrip(tripId);
  } catch {
    // error handled by ErrorState
  }
  document.addEventListener("keydown", onKeydown);
  socket.connect();
  membersCtx.fetchMembers();
  budget.fetchBudget();
  fetchBudgetExpenses();
  memoriesCtx.fetchMemories();
  fetchPois();
});
onUnmounted(() => {
  document.removeEventListener("keydown", onKeydown);
  clearTimeout(geoTimeout);
});

</script>

<template>
    <OfflineBanner />
  <div class="min-h-screen bg-gray-50" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="(e: TouchEvent) => { onTouchEnd(); onSwipeEnd(e); }">
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
    <!-- Hero Banner -->
    <header class="bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 text-white shadow-lg">
      <div class="mx-auto max-w-6xl px-3 md:px-4 py-3 md:py-4">
        <!-- Top row: back, title, actions -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3 min-w-0">
            <button @click="router.push('/')" class="text-white/80 hover:text-white text-lg flex-shrink-0">←</button>
            <h1 class="text-xl font-bold truncate" v-if="tripStore.currentTrip">
              {{ tripStore.currentTrip.title }}
            </h1>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span
              v-if="socket.connected.value"
              class="flex items-center gap-1 rounded-full bg-white/10 backdrop-blur-sm px-2.5 py-1 text-xs text-white/90"
              title="已連線"
            >
              <span class="h-1.5 w-1.5 rounded-full bg-green-400"></span>
              {{ socket.users.value.length }} 人在線
            </span>
            <button
              @click="showMemberModal = true"
              class="rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-sm text-white/90 hover:bg-white/20 transition"
            >
              👥 成員
            </button>
            <button
              @click="showShareModal = true"
              class="rounded-lg bg-white/10 backdrop-blur-sm px-3 py-1.5 text-sm text-white/90 hover:bg-white/20 transition"
            >
              🔗 分享
            </button>
            <span class="text-sm text-white/80 ml-1">{{ auth.user?.name }}</span>
            <button @click="toggleDark" class="text-sm text-white/60 hover:text-white transition ml-1" :title="isDark ? '切換亮色' : '切換暗色'">{{ isDark ? '☀️' : '🌙' }}</button>
          </div>
        </div>
        <!-- Hero info row -->
        <div class="mt-3 flex flex-wrap items-center gap-3 text-white/80 text-sm">
          <span class="inline-flex items-center gap-1">📅 {{ tripStore.currentTrip?.start_date }} ~ {{ tripStore.currentTrip?.end_date }}</span>
          <span v-if="tripStore.currentTrip?.destination_country" class="inline-flex items-center gap-1 rounded-full bg-white/20 px-2.5 py-0.5 text-xs font-medium text-white/90">
            🌍 {{ tripStore.currentTrip?.destination_country }}
          </span>
          <span v-if="tripStore.currentTrip?.destination_tz_offset !== null" class="inline-flex items-center gap-1 rounded-full bg-white/20 px-2.5 py-0.5 text-xs font-medium text-white/90">
            🕐 UTC{{ (tripStore.currentTrip?.destination_tz_offset ?? 0) >= 0 ? '+' : '' }}{{ tripStore.currentTrip?.destination_tz_offset }}
          </span>
          <span v-if="!navigatorObj.onLine" class="inline-flex items-center gap-1 rounded-full bg-amber-500/20 px-2 py-0.5 text-xs text-amber-200">
            ⚠️ 離線
          </span>
        </div>        <!-- Trip Stats -->
        <div v-if="tripStats && activeTab === 'itinerary'" class="mt-3 flex flex-wrap gap-2">
          <span class="inline-flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-0.5 text-xs text-white/90">
            📅 {{ tripStats.durationDays }} 天
          </span>
          <span class="inline-flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-0.5 text-xs text-white/90">
            📍 {{ tripStats.totalActivities }} 個活動
          </span>
          <span v-if="tripStats.locations > 0" class="inline-flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-0.5 text-xs text-white/90">
            🏙️ {{ tripStats.locations }} 個地點
          </span>
          <span v-if="tripStats.totalExpenses > 0" class="inline-flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-0.5 text-xs text-white/90">
            💰 ${{ tripStats.totalExpenses.toLocaleString() }}
          </span>
          <span v-if="tripStats.photosCount > 0" class="inline-flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-0.5 text-xs text-white/90">
            📸 {{ tripStats.photosCount }} 張照片
          </span>
        </div>
      </div>
    </header>

    <!-- Tab Bar -->
    <div class="border-b border-gray-200 bg-white shadow-sm">
      <div class="mx-auto hidden md:flex max-w-6xl px-4">
        <button
          @click="activeTab = 'itinerary'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'itinerary' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          📅 行程
          <span v-if="activeTab === 'itinerary'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
        <button
          @click="activeTab = 'map'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'map' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          🗺️ 地圖
          <span v-if="activeTab === 'map'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
        <button
          @click="activeTab = 'budget'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'budget' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          💰 預算
          <span v-if="activeTab === 'budget'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
        <button
          @click="activeTab = 'memories'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'memories' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          📝 回憶
          <span v-if="activeTab === 'memories'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
        <button
          @click="activeTab = 'poi'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'poi' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          📍 景點
          <span v-if="activeTab === 'poi'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
        <button
          @click="activeTab = 'packing'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'packing' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          🎒 打包
          <span v-if="activeTab === 'packing'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
        <button
          @click="activeTab = 'photos'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'photos' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          📸 相簿
          <span v-if="activeTab === 'photos'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
        <button
          @click="activeTab = 'polls'"
          :class="[
            'px-6 py-3 text-sm font-medium transition relative',
            activeTab === 'polls' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700',
          ]"
        >
          📊 投票
          <span v-if="activeTab === 'polls'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500"></span>
        </button>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="tripStore.loading" class="mx-auto max-w-lg py-12 px-4">
      <SkeletonLoader hasAvatar :lines="4" />
      <div class="mt-6">
        <SkeletonLoader :lines="5" hasImage />
      </div>
    </div>

    <ErrorState v-else-if="tripStore.currentTrip === null && !tripStore.loading && tripStore.days.length === 0" />

    <!-- Content -->
    <div v-else class="mx-auto max-w-6xl px-4 py-6 pb-20 md:pb-0">
      <!-- Today Summary Card -->
      <div v-if="todaySummary" class="mb-6 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 p-5 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-white/80">📅 今日行程</p>
            <p class="text-lg font-bold mt-0.5">{{ todaySummary.date }}</p>
            <p v-if="todaySummary.dayTitle" class="text-sm text-white/80 mt-0.5">{{ todaySummary.dayTitle }}</p>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold">{{ todaySummary.activityCount }}</p>
            <p class="text-xs text-white/80">個活動</p>
          </div>
        </div>
      </div>

      <!-- ========== ITINERARY TAB (Timeline) ========== -->
      <div v-show="activeTab === 'itinerary'" class="flex flex-col lg:flex-row gap-6">
        <!-- Left: Itinerary -->
        <div class="flex-1 min-w-0">
        <VueDraggable v-model="tripStore.days" ghost-class="opacity-30" @end="() => tripStore.reorderDays(tripStore.days.map(d => d.id))">
          <div
            v-for="day in tripStore.days"
            :key="day.id"
            class="relative flex gap-4 pb-8 cursor-grab active:cursor-grabbing"
          >
            <!-- Timeline line and dot -->
            <div class="flex flex-col items-center">
              <div class="h-4 w-4 rounded-full border-2 border-indigo-400 bg-white z-10"></div>
              <div class="w-0.5 flex-1 bg-indigo-200 mt-1"></div>
            </div>

            <!-- Day content -->
            <div class="flex-1 min-w-0">
              <!-- Day header -->
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-gray-900">{{ day.date }}</span>
                  <span v-if="day.title" class="text-sm text-gray-500">· {{ day.title }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="openNewActivity(day.id)"
                    class="rounded-lg bg-indigo-600 px-3 py-1 text-xs text-white hover:bg-indigo-700"
                  >
                    ＋ 活動
                  </button>
                  <button
                    @click="confirmDeleteDay(day.id)"
                    class="text-gray-300 hover:text-red-500 text-xs"
                    title="刪除天數"
                  >
                    ✕
                  </button>
                </div>
              </div>

              <!-- Activities (draggable) -->
              <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                <EmptyState v-if="(tripStore.activities[day.id] || []).length === 0" icon="📅" title="還沒有活動" description="按「＋ 活動」新增第一個行程" @action="openNewActivity(day.id)" />
                <VueDraggable v-else v-model="tripStore.activities[day.id]" ghost-class="opacity-30" class="divide-y divide-gray-50" @end="() => tripStore.reorderActivities(day.id, (tripStore.activities[day.id] || []).map(a => a.id))">
                  <div
                    v-for="act in (tripStore.activities[day.id] || [])"
                    :key="act.id"
                    class="group flex items-start gap-3 px-4 py-3 hover:bg-gray-50 cursor-grab active:cursor-grabbing"
                  >
                    <!-- Time badge -->
                    <div class="w-14 flex-shrink-0 rounded bg-gray-100 px-1.5 py-0.5 text-center text-xs font-medium text-gray-500">
                      {{ act.start_time || '--:--' }}{{ act.end_time ? ' - ' + act.end_time : '' }}
                    </div>

                    <!-- Category badge -->
                    <span
                      :class="['rounded px-1.5 py-0.5 text-xs font-medium flex-shrink-0', CATEGORY_COLORS[act.category]]"
                    >
                      {{ CATEGORY_LABELS[act.category] }}
                    </span>

                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900">{{ act.title }}</p>
                      <p v-if="act.notes" class="text-xs text-gray-400 mt-0.5 truncate">{{ act.notes }}</p>
                    </div>

                    <!-- Actions -->
                    <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition flex-shrink-0">
                      <button @click="openEditActivity(act)" class="text-gray-300 hover:text-indigo-500 text-xs" title="編輯">✏️</button>
                      <button @click="confirmDeleteActivity(act.id)" class="text-gray-300 hover:text-red-500 text-xs" title="刪除">✕</button>
                    </div>
                  </div>
                </VueDraggable>
              </div>
            </div>
          </div>
        </VueDraggable>

        <!-- Add day button -->
        <button
          @click="showNewDay = true"
          class="mt-2 w-full rounded-xl border-2 border-dashed border-gray-300 py-4 text-sm text-gray-400 hover:border-indigo-400 hover:text-indigo-500 transition"
        >
          ＋ 新增天數
        </button>
        </div>
        <!-- End left: Itinerary -->

        <!-- Right: Map (desktop only, side-by-side with itinerary) -->
        <div class="hidden lg:block lg:w-[420px] xl:w-[500px] flex-shrink-0">
          <div class="sticky top-4 h-[calc(100vh-12rem)] rounded-xl overflow-hidden border border-gray-200 shadow-sm">
            <TripMap :markers="mapMarkers" :poi-markers="poiMarkers" :route-data="routeData" :center="mapCenter" :zoom="mapZoom" />
          </div>
        </div>
      </div>

      <!-- ========== MAP TAB ========== -->
      <div v-show="activeTab === 'map'" class="h-[70vh] rounded-xl overflow-hidden border border-gray-200">
        <TripMap :markers="mapMarkers" :poi-markers="poiMarkers" :route-data="routeData" :center="mapCenter" :zoom="mapZoom" />
      </div>

      <!-- ========== BUDGET TAB ========== -->
      <div v-show="activeTab === 'budget'">
        <!-- Budget tab header -->
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">預算明細</h2>
          <button
            @click="openAddExpense(auth.user?.id)"
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
          >
            ＋ 開銷
          </button>
          <button
            @click="fetchSettleUp"
            :disabled="settleLoading"
            class="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition"
          >
            {{ settleLoading ? '計算中...' : '🧮 結算' }}
          </button>
        </div>
        <div v-if="budgetLoading" class="py-12 text-center text-gray-400">
          <p class="text-2xl mb-2 animate-pulse">💰</p>
          <p class="text-sm">載入預算資料...</p>
        </div>
        <div v-else-if="!budgetData" class="rounded-xl border border-gray-200 bg-white py-12 text-center shadow-sm">
          <p class="text-3xl mb-2">📭</p>
          <p class="text-sm text-gray-400">尚無預算資料</p>
        </div>
        <div v-else class="space-y-6">
          <!-- Total -->
          <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <p class="text-xs text-gray-500 mb-1">總預算</p>
            <p class="text-3xl font-bold text-gray-900">${{ budgetData.total_expenses.toLocaleString() }}</p>
          </div>

          <!-- By category breakdown -->
          <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h3 class="text-sm font-semibold text-gray-700 mb-4">分類支出</h3>
            <div class="space-y-3">
              <div v-for="(total, category) in budgetData.by_category" :key="category" class="flex items-center justify-between">
                <span class="text-sm text-gray-600">{{ BUDGET_LABELS[category] || category }}</span>
                <div class="flex items-center gap-3">
                  <div class="h-2 w-32 rounded-full bg-gray-100 overflow-hidden">
                    <div
                      class="h-full rounded-full bg-indigo-400"
                      :style="{ width: budgetData.total_expenses > 0 ? (total / budgetData.total_expenses * 100) + '%' : '0%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-gray-900 w-20 text-right">${{ total.toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Per-person balances -->
          <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h3 class="text-sm font-semibold text-gray-700 mb-4">人均分攤</h3>
            <div class="space-y-2">
              <div v-for="(amount, name) in budgetData.per_person" :key="name" class="flex items-center justify-between py-1">
                <span class="text-sm text-gray-600">{{ name }}</span>
                <span class="text-sm font-medium text-gray-900">${{ amount.toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <!-- Expense list -->
          <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h3 class="text-sm font-semibold text-gray-700 mb-4">支出明細</h3>
            <div v-if="expensesLoading" class="py-4 text-center text-xs text-gray-400">載入中...</div>
            <div v-else-if="expenses.length === 0" class="py-4 text-center text-xs text-gray-300">尚無支出紀錄</div>
            <div v-else class="divide-y divide-gray-50">
              <div v-for="expense in expenses" :key="expense.id" class="flex items-center justify-between py-3">
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900">{{ expense.title }}</p>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span class="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600">{{ BUDGET_LABELS[expense.category] || expense.category }}</span>
                    <span class="text-xs text-gray-400">由 {{ expense.paid_by_name }} 付款</span>
                    <span v-if="expense.splits && expense.splits.length > 0" class="text-xs text-gray-400">· 與 {{ expense.splits.length }} 人分攤</span>
                  </div>
                </div>
                <div class="flex items-center gap-3 flex-shrink-0">
                  <span class="text-sm font-medium text-gray-900">${{ expense.amount.toLocaleString() }}</span>
                  <button
                    @click="handleDeleteExpense(expense.id)"
                    class="text-gray-200 hover:text-red-500 text-xs"
                    title="刪除"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== MEMORIES TAB ========== -->
      <div v-show="activeTab === 'memories'">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">📝 旅程回憶</h2>
          <button
            @click="showAddMemory = true"
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
          >
            ＋ 回憶
          </button>
        </div>

        <div v-if="memoriesLoading" class="py-12 text-center text-gray-400">
          <p class="text-3xl mb-2 animate-pulse">📝</p>
          <p class="text-sm">載入回憶...</p>
        </div>

        <div v-else-if="memories.length === 0" class="rounded-xl border border-gray-200 bg-white py-12 text-center shadow-sm">
          <p class="text-5xl mb-3">📭</p>
          <p class="text-sm text-gray-400">還沒有回憶，開始記錄你的旅程吧！</p>
        </div>

        <!-- Memory Timeline -->
        <div v-else class="space-y-4">
          <div
            v-for="memory in memories"
            :key="memory.id"
            class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xs text-gray-400">{{ memory.date }}</span>
                  <span class="text-xs text-gray-300">·</span>
                  <span class="text-xs text-gray-400">{{ memory.user_name }}</span>
                </div>
                <h3 class="text-base font-bold text-gray-900">{{ memory.title }}</h3>
                <p v-if="memory.content" class="mt-1 text-sm text-gray-600 whitespace-pre-wrap">{{ memory.content }}</p>
                <div v-if="memory.photo_urls && memory.photo_urls.length > 0" class="mt-3 flex gap-2 overflow-x-auto">
                  <img v-for="(url, i) in memory.photo_urls" :key="i" :src="url" class="h-20 w-20 flex-shrink-0 rounded-lg object-cover border border-gray-200" />
                </div>
              </div>
              <button
                @click="handleDeleteMemory(memory.id)"
                class="ml-2 text-gray-200 hover:text-red-500 text-xs flex-shrink-0"
                title="刪除"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== POI TAB ========== -->
      <div v-show="activeTab === 'poi'" class="space-y-6">
        <POIManager :trip-id="tripId" />
        <RoutePlanner :trip-id="tripId" :pois="pois" @route="onRoute" />
      </div>

      <!-- ========== PACKING TAB ========== -->
      <div v-show="activeTab === 'packing'">
        <PackingList :trip-id="tripId" />
      </div>

      <!-- ========== POLLS TAB ========== -->
      <div v-show="activeTab === 'polls'">
        <PollCard :trip-id="tripId" />
      </div>

      <!-- ========== PHOTOS TAB ========== -->
      <div v-show="activeTab === 'photos'">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">📸 相簿</h2>
          <span class="text-sm text-gray-400">{{ allTripPhotos.length }} 張照片</span>
        </div>
        <div v-if="allTripPhotos.length === 0" class="py-16 text-center">
          <p class="text-5xl mb-3">📸</p>
          <p class="text-sm text-gray-400">還沒有照片，開始記錄你的旅程吧！</p>
        </div>
        <div v-else class="columns-2 md:columns-3 gap-3 space-y-3">
          <div v-for="(photo, i) in allTripPhotos" :key="i" class="break-inside-avoid rounded-xl overflow-hidden shadow-sm border border-gray-200 bg-white">
            <img :src="photo.url" class="w-full object-cover" loading="lazy" />
            <div class="px-3 py-2">
              <p class="text-xs text-gray-500">{{ photo.user_name }} · {{ photo.date }}</p>
            </div>
          </div>
        </div>
      </div>

    </div>

    <QuickNote ref="quickNoteRef" :trip-id="tripId" @saved="memoriesCtx.fetchMemories" />

    <ConfirmModal
      :show="showDeleteConfirm"
      title="確認刪除"
      :message="deletingActivityId ? '確定要刪除此活動？' : '確定要刪除此天數及其所有活動？'"
      confirm-text="刪除"
      cancel-text="取消"
      variant="danger"
      @confirm="handleDeleteConfirm"
      @cancel="showDeleteConfirm = false"
    />

<!-- ========== ADD MEMORY MODAL ========== -->
    <!-- Mobile Bottom Nav -->
    <div class="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 bg-white md:hidden safe-area-bottom">
      <div class="flex overflow-x-auto scrollbar-hide">
        <button @click="activeTab = 'itinerary'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'itinerary' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">📅</span>
          <span>行程</span>
        </button>
        <button @click="activeTab = 'map'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'map' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">🗺️</span>
          <span>地圖</span>
        </button>
        <button @click="activeTab = 'budget'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'budget' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">💰</span>
          <span>預算</span>
        </button>
        <button @click="activeTab = 'memories'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'memories' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">📝</span>
          <span>回憶</span>
        </button>
        <button @click="activeTab = 'poi'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'poi' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">📍</span>
          <span>景點</span>
        </button>
        <button @click="activeTab = 'packing'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'packing' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">🎒</span>
          <span>打包</span>
        </button>
        <button @click="activeTab = 'photos'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'photos' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">📸</span>
          <span>相簿</span>
        </button>
        <button @click="activeTab = 'polls'" class="flex-shrink-0 flex flex-col items-center px-4 py-2 text-xs"
          :class="activeTab === 'polls' ? 'text-indigo-600' : 'text-gray-400'">
          <span class="text-lg">📊</span>
          <span>投票</span>
        </button>
      </div>
    </div>

      <div v-if="showAddMemory" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showAddMemory = false">
        <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
          <h3 class="mb-4 text-lg font-bold">新增回憶</h3>
          <form @submit.prevent="handleAddMemory" class="space-y-3">
            <input v-model="newMemTitle" placeholder="標題" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <input v-model="newMemDate" type="date" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <textarea v-model="newMemContent" rows="3" placeholder="寫下你的回憶..." class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"></textarea>
            <div class="space-y-2">
              <div class="flex flex-wrap gap-2">
                <div v-for="(photo, i) in newMemPhotos" :key="i" class="relative h-20 w-20 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                  <img :src="photo" class="h-full w-full object-cover" />
                  <button @click="removePhoto(i)" type="button" class="absolute top-0.5 right-0.5 h-5 w-5 rounded-full bg-black/50 text-white text-xs flex items-center justify-center">✕</button>
                </div>
                <label v-if="newMemPhotos.length < 9" class="flex h-20 w-20 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 hover:border-indigo-400">
                  <span class="text-2xl text-gray-400">📷</span>
                  <span class="text-xs text-gray-400">拍照/選取</span>
                  <input type="file" accept="image/*" capture multiple class="hidden" @change="handleFileSelect" />
                </label>
              </div>
            </div>
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" @click="showAddMemory = false" class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">取消</button>
              <button type="submit" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">新增</button>
            </div>
          </form>
        </div>
      </div>

    <!-- ========== EDIT ACTIVITY MODAL ========== -->
    <div v-if="showEditActivity" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showEditActivity = false">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">✏️ 編輯活動</h3>
        <form @submit.prevent="handleUpdateActivity" class="space-y-3">
          <input v-model="editActTitle" placeholder="活動名稱" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500" />

          <div class="flex gap-2">
            <div class="flex-1">
              <label class="block text-xs text-gray-500">類別</label>
              <select v-model="editActCategory" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                <option v-for="(label, key) in CATEGORY_LABELS" :key="key" :value="key">{{ label }}</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-xs text-gray-500">開始</label>
              <input v-model="editActStartTime" type="time" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div class="flex-1">
              <label class="block text-xs text-gray-500">結束</label>
              <input v-model="editActEndTime" type="time" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>

          <div>
            <label class="block text-xs text-gray-500">交通方式</label>
            <select v-model="editActTransportMode" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="">無</option>
              <option value="flight">✈️ 航班</option>
              <option value="train">🚄 火車</option>
              <option value="bus">🚌 巴士</option>
              <option value="ferry">⛴️ 渡輪</option>
              <option value="car">🚗 自駕</option>
            </select>
          </div>

          <div>
            <label class="block text-xs text-gray-500">負責人</label>
            <select v-model="editActAssignee" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="">未指定</option>
              <option v-for="m in members" :key="m.user_id" :value="m.user_id">{{ m.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs text-gray-500">備註</label>
            <textarea v-model="editActNotes" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" placeholder="可選"></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showEditActivity = false" class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">取消</button>
            <button type="submit" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">儲存</button>
          </div>
        </form>
      </div>
    </div>

<!-- ========== NEW DAY MODAL ========== -->
    <div v-if="showNewDay" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showNewDay = false">
      <div class="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">新增天數</h3>
        <form @submit.prevent="handleCreateDay" class="space-y-3">
          <input v-model="newDayDate" type="date" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
          <input v-model="newDayTitle" placeholder="標題（選填）" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showNewDay = false" class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">取消</button>
            <button type="submit" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">新增</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========== NEW ACTIVITY MODAL ========== -->
    <div v-if="showNewActivity" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showNewActivity = false">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">新增活動</h3>
        <form @submit.prevent="handleCreateActivity" class="space-y-3">
          <input v-model="newActTitle" placeholder="活動名稱" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />

          <div class="flex gap-2">
            <div class="flex-1">
              <label class="block text-xs text-gray-500">類別</label>
              <select v-model="newActCategory" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                <option v-for="(label, key) in CATEGORY_LABELS" :key="key" :value="key">{{ label }}</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-xs text-gray-500">開始</label>
              <input v-model="newActTime" type="time" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div class="flex-1">
              <label class="block text-xs text-gray-500">結束</label>
              <input v-model="newActEndTime" type="time" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>

          <div>
            <label class="block text-xs text-gray-500">交通方式</label>
            <select v-model="newActTransportMode" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="">無</option>
              <option value="flight">✈️ 航班</option>
              <option value="train">🚄 火車</option>
              <option value="bus">🚌 巴士</option>
              <option value="ferry">⛴️ 渡輪</option>
              <option value="car">🚗 自駕</option>
            </select>
          </div>

          <div>
            <label class="block text-xs text-gray-500">負責人</label>
            <select v-model="newActAssignee" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="">未指定</option>
              <option v-for="m in members" :key="m.user_id" :value="m.user_id">{{ m.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs text-gray-500">備註</label>
            <textarea v-model="newActNotes" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" placeholder="可選"></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showNewActivity = false" class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">取消</button>
            <button type="submit" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">新增</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========== MEMBERS MODAL ========== -->
    <div v-if="showMemberModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showMemberModal = false">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">👥 成員管理</h3>

        <div class="mb-4">
          <p class="text-xs text-gray-500 mb-2">線上成員</p>
          <div v-if="socket.users.value.length === 0" class="text-xs text-gray-300">無其他在線成員</div>
          <div v-for="u in socket.users.value" :key="u.user_id" class="flex items-center gap-2 py-1">
            <span class="h-2 w-2 rounded-full bg-green-500"></span>
            <span class="text-sm">{{ u.user_name }}</span>
          </div>
        </div>

        <div class="mb-4">
          <p class="text-xs text-gray-500 mb-2">所有成員</p>
          <div v-for="m in members" :key="m.id" class="flex items-center justify-between py-1.5">
            <div class="flex items-center gap-2">
              <span class="text-sm">{{ m.name }}</span>
              <span class="text-xs text-gray-400">({{ m.email }})</span>
              <span v-if="m.role === 'owner'" class="rounded bg-yellow-100 px-1.5 py-0.5 text-xs text-yellow-700">擁有者</span>
              <span v-else class="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700">{{ m.role }}</span>
            </div>
          </div>
        </div>

        <div class="border-t border-gray-100 pt-4">
          <p class="text-xs text-gray-500 mb-2">透過 Email 邀請成員</p>
          <form @submit.prevent="handleInvite" class="flex gap-2">
            <input
              v-model="inviteEmail"
              type="email"
              placeholder="friend@example.com"
              required
              class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
            <button type="submit" class="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white hover:bg-indigo-700">
              邀請
            </button>
          </form>
          <p v-if="inviteMsg" class="mt-2 text-xs" :class="inviteMsg.includes('成功') ? 'text-green-600' : 'text-red-600'">
            {{ inviteMsg }}
          </p>
        </div>

        <button @click="showMemberModal = false" class="mt-4 w-full rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50">
          關閉
        </button>
      </div>
    </div>

    <!-- ========== SHARE MODAL ========== -->
    <div v-if="showShareModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showShareModal = false">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">🔗 分享行程</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between rounded-lg bg-gray-100 px-4 py-3">
            <span class="text-sm font-medium">
              {{ tripStore.currentTrip?.visibility === 'shared' ? '🔓 分享中' : '🔒 私人' }}
            </span>
            <button
              @click="handleToggleShare"
              :class="[
                'rounded-lg px-3 py-1 text-xs font-medium transition',
                tripStore.currentTrip?.visibility === 'shared'
                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                  : 'bg-green-100 text-green-700 hover:bg-green-200',
              ]"
            >
              {{ tripStore.currentTrip?.visibility === 'shared' ? '關閉分享' : '開啟分享' }}
            </button>
          </div>

          <div v-if="tripStore.currentTrip?.visibility === 'shared'">
            <label class="block text-xs text-gray-500 mb-1">分享連結</label>
            <div class="flex gap-2">
              <input :value="shareUrl" readonly class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm bg-gray-50" />
              <button
                @click="copyShareUrl()"
                class="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white hover:bg-indigo-700"
              >
                複製
              </button>
            </div>
          </div>
          <!-- Invite link section -->
          <div v-if="tripStore.currentTrip?.visibility === 'shared'" class="mt-4 border-t border-gray-100 pt-4">
            <label class="block text-xs text-gray-500 mb-1">邀請連結</label>
            <div class="flex gap-2">
              <input 
                :value="inviteUrl" 
                readonly 
                class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm bg-gray-50" 
              />
              <button
                @click="copyInviteLink"
                class="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white hover:bg-indigo-700"
              >
                複製
              </button>
            </div>
            <p class="mt-2 text-xs text-gray-400">分享此連結給好友，他們不需註冊即可加入行程</p>
          </div>

          <!-- Export itinerary section -->
          <div class="mt-4 border-t border-gray-100 pt-4">
            <label class="block text-xs text-gray-500 mb-2">匯出行程</label>
            <button
              @click="exportItinerary()"
              class="w-full rounded-lg bg-gray-100 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-200 transition flex items-center justify-center gap-2"
            >
              📋 複製為純文字
            </button>
            <p class="mt-1 text-xs text-gray-400">複製行程表到剪貼簿，可貼到 LINE、備忘錄等</p>
          </div>
          <button @click="showShareModal = false" class="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50">
            關閉
          </button>
        </div>
      </div>
    </div>

    <!-- Settle Up Modal -->
    <div v-if="showSettleUp" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showSettleUp = false">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold">💰 結算計畫</h3>
          <button @click="showSettleUp = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div v-if="!settleUpData || settleUpData.transactions.length === 0" class="py-8 text-center text-gray-400">
          <p class="text-3xl mb-2">✅</p>
          <p class="text-sm">無人需要結算，所有人已平分</p>
        </div>
        <div v-else class="space-y-3">
          <div v-for="(t, i) in settleUpData.transactions" :key="i"
            class="flex items-center justify-between rounded-lg bg-gray-50 p-4">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-red-600">{{ t.from_user_name }}</span>
              <span class="text-gray-400">→</span>
              <span class="text-sm font-medium text-green-600">{{ t.to_user_name }}</span>
            </div>
            <span class="text-sm font-bold text-gray-900">${{ t.amount.toLocaleString() }}</span>
          </div>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <button @click="copySettleUp" v-if="settleUpData?.transactions.length" class="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50">📋 複製</button>
          <button @click="showSettleUp = false" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700">關閉</button>
        </div>
    </div>
  </div>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
