<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { poiApi } from "../api/client";
import type { POI } from "../types";
import SkeletonLoader from "./SkeletonLoader.vue";
import EmptyState from "./EmptyState.vue";
import ErrorState from "./ErrorState.vue";
import { usePhotoUpload } from "../composables/usePhotoUpload";

const props = defineProps<{
  tripId: string;
}>();

const pois = ref<POI[]>([]);
const loading = ref(false);
const error = ref(false);

const activeFilter = ref<string>("all");
const showAddModal = ref(false);
const showEditModal = ref(false);
const editingPoi = ref<POI | null>(null);

// Add form
const newName = ref("");
const newCategory = ref("attraction");
const newAddress = ref("");
const newNotes = ref("");

const { uploading, photos, handleFileSelect, removePhoto, uploadPhotos, reset } = usePhotoUpload();

function extractImageUrls(notes: string | null): string[] {
  if (!notes) return [];
  const urls: string[] = [];
  const re = /!\[.*?\]\((.*?)\)/g;
  let m;
  while ((m = re.exec(notes)) !== null) {
    urls.push(m[1]);
  }
  return urls;
}

// Edit form
const editName = ref("");
const editCategory = ref("attraction");
const editAddress = ref("");
const editNotes = ref("");

const POI_CATEGORIES = ["attraction", "food", "shopping", "other"] as const;

const POI_CATEGORY_LABELS: Record<string, string> = {
  attraction: "🏛️ 景點",
  food: "🍜 美食",
  shopping: "🛍️ 購物",
  other: "📌 其他",
};

const POI_CATEGORY_COLORS: Record<string, string> = {
  attraction: "bg-purple-100 text-purple-800",
  food: "bg-orange-100 text-orange-800",
  shopping: "bg-pink-100 text-pink-800",
  other: "bg-gray-100 text-gray-800",
};

const filteredPois = computed(() => {
  if (activeFilter.value === "all") return pois.value;
  return pois.value.filter((p: POI) => p.category === activeFilter.value);
});

async function fetchPois() {
  loading.value = true;
  error.value = false;
  try {
    const res = await poiApi.list(props.tripId);
    pois.value = res.data;
  } catch {
    error.value = true;
    pois.value = [];
  } finally {
    loading.value = false;
  }
}

function openAddModal() {
  newName.value = "";
  newCategory.value = "attraction";
  newAddress.value = "";
  newNotes.value = "";
  reset();
  showAddModal.value = true;
}

async function handleAdd() {
  if (!newName.value) return;
  try {
    let notes = newNotes.value || "";
    if (photos.value.length > 0) {
      const urls = await uploadPhotos();
      const photoMd = urls.map((u: string) => `![](${u})`).join("\n");
      notes = notes ? `${notes}\n\n${photoMd}` : photoMd;
    }
    await poiApi.create(props.tripId, {
      name: newName.value,
      category: newCategory.value,
      address: newAddress.value || undefined,
      notes: notes || undefined,
    });
    showAddModal.value = false;
    reset();
    await fetchPois();
  } catch {
    // ignore
  }
}

function openEditModal(poi: POI) {
  editingPoi.value = poi;
  editName.value = poi.name;
  editCategory.value = poi.category;
  editAddress.value = poi.address || "";
  editNotes.value = poi.notes || "";
  showEditModal.value = true;
}

async function handleUpdate() {
  if (!editingPoi.value || !editName.value) return;
  try {
    await poiApi.update(editingPoi.value.id, {
      name: editName.value,
      category: editCategory.value,
      address: editAddress.value || undefined,
      notes: editNotes.value || undefined,
    });
    showEditModal.value = false;
    editingPoi.value = null;
    await fetchPois();
  } catch {
    // ignore
  }
}

async function handleDelete(poiId: string) {
  try {
    await poiApi.delete(poiId);
    await fetchPois();
  } catch {
    // ignore
  }
}

onMounted(() => {
  fetchPois();
});
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-900">📍 興趣點</h2>
      <button
        @click="openAddModal"
        class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
      >
        ＋ POI
      </button>
    </div>

    <!-- Filter Tabs -->
    <div class="mb-4 flex gap-2 overflow-x-auto">
      <button
        @click="activeFilter = 'all'"
        :class="[
          'whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition',
          activeFilter === 'all'
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
        ]"
      >
        全部
      </button>
      <button
        v-for="cat in POI_CATEGORIES"
        :key="cat"
        @click="activeFilter = cat"
        :class="[
          'whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition',
          activeFilter === cat
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
        ]"
      >
        {{ POI_CATEGORY_LABELS[cat] }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i">
        <SkeletonLoader :lines="2" />
      </div>
    </div>

    <!-- Error -->
    <ErrorState
      v-else-if="error"
      message="無法載入興趣點"
      retryText="重試"
      @retry="fetchPois"
    />

    <!-- Empty -->
    <EmptyState
      v-else-if="filteredPois.length === 0"
      icon="📍"
      title="尚無興趣點"
      description="按「＋ POI」新增第一個地點"
      actionText="新增 POI"
      @action="openAddModal"
    />

    <!-- POI List -->
    <div v-else class="space-y-3">
      <div
        v-for="poi in filteredPois"
        :key="poi.id"
        class="group rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-xl"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="text-base font-bold text-gray-900">{{ poi.name }}</h3>
              <span
                :class="['rounded px-1.5 py-0.5 text-xs font-medium', POI_CATEGORY_COLORS[poi.category] || POI_CATEGORY_COLORS.other]"
              >
                {{ POI_CATEGORY_LABELS[poi.category] || poi.category }}
              </span>
            </div>
            <p v-if="poi.address" class="text-xs text-gray-500 truncate">{{ poi.address }}</p>
            <div v-if="extractImageUrls(poi.notes).length" class="flex gap-1 mt-1">
              <img
                v-for="url in extractImageUrls(poi.notes).slice(0, 3)"
                :key="url"
                :src="url"
                class="h-14 w-14 rounded-lg object-cover"
              />
            </div>
            <p v-if="poi.notes" class="mt-1 text-xs text-gray-400 line-clamp-2">{{ poi.notes }}</p>
          </div>
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition flex-shrink-0 ml-2">
            <button
              @click="openEditModal(poi)"
              class="text-gray-300 hover:text-indigo-500 text-xs"
              title="編輯"
            >
              ✏️
            </button>
            <button
              @click="handleDelete(poi.id)"
              class="text-gray-300 hover:text-red-500 text-xs"
              title="刪除"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== ADD MODAL ========== -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="showAddModal = false"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">新增興趣點</h3>
        <form @submit.prevent="handleAdd" class="space-y-3">
          <input
            v-model="newName"
            placeholder="名稱"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
          />

          <div>
            <label class="block text-xs text-gray-500">類別</label>
            <select
              v-model="newCategory"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option v-for="cat in POI_CATEGORIES" :key="cat" :value="cat">
                {{ POI_CATEGORY_LABELS[cat] }}
              </option>
            </select>
          </div>

          <input
            v-model="newAddress"
            placeholder="地址（選填）"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />

          <div>
            <label class="block text-xs text-gray-500">備註（選填）</label>
            <textarea
              v-model="newNotes"
              rows="2"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              placeholder="可選"
            ></textarea>
          </div>

          <!-- Photo picker -->
          <div class="space-y-2">
            <label class="block text-xs text-gray-500">照片（最多 9 張，選填）</label>
            <div v-if="photos.length" class="grid grid-cols-3 gap-2">
              <div v-for="(photo, i) in photos" :key="i" class="relative">
                <img :src="photo" class="h-20 w-full rounded-lg object-cover" />
                <button
                  type="button"
                  @click="removePhoto(i)"
                  class="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white"
                >
                  ✕
                </button>
              </div>
            </div>
            <label
              v-if="photos.length < 9"
              class="flex h-20 cursor-pointer items-center justify-center rounded-lg border-2 border-dashed border-gray-300 hover:border-indigo-400"
            >
              <input
                type="file"
                accept="image/*"
                capture="environment"
                multiple
                class="hidden"
                @change="handleFileSelect"
              />
              <span class="text-xs text-gray-400">＋ 新增照片</span>
            </label>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              @click="showAddModal = false"
              class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100"
            >
              取消
            </button>
            <button
              type="submit"
              class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
            >
              新增
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========== EDIT MODAL ========== -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="showEditModal = false"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">✏️ 編輯興趣點</h3>
        <form @submit.prevent="handleUpdate" class="space-y-3">
          <input
            v-model="editName"
            placeholder="名稱"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
          />

          <div>
            <label class="block text-xs text-gray-500">類別</label>
            <select
              v-model="editCategory"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option v-for="cat in POI_CATEGORIES" :key="cat" :value="cat">
                {{ POI_CATEGORY_LABELS[cat] }}
              </option>
            </select>
          </div>

          <input
            v-model="editAddress"
            placeholder="地址（選填）"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />

          <div>
            <label class="block text-xs text-gray-500">備註（選填）</label>
            <textarea
              v-model="editNotes"
              rows="2"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              placeholder="可選"
            ></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              @click="showEditModal = false"
              class="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100"
            >
              取消
            </button>
            <button
              type="submit"
              class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
            >
              儲存
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
