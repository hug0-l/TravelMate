<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { packingApi } from "../api/client";
import type { PackingItem } from "../types";
import SkeletonLoader from "./SkeletonLoader.vue";
import EmptyState from "./EmptyState.vue";
import { useToast } from "../composables/useToast";

const props = defineProps<{
  tripId: string;
}>();

const { add: addToast } = useToast();

const items = ref<PackingItem[]>([]);
const loading = ref(false);
const activeFilter = ref<string>("all");
const showAddModal = ref(false);
const newName = ref("");
const newCategory = ref("clothing");
const newQuantity = ref(1);

const PACKING_CATEGORIES = ["clothing", "toiletries", "electronics", "medicine", "document", "other"] as const;

const CATEGORY_FILTERS: { key: string; label: string }[] = [
  { key: "all", label: "📋 全部" },
  { key: "clothing", label: "👕 衣物" },
  { key: "toiletries", label: "🧴 盥洗" },
  { key: "electronics", label: "📱 3C" },
  { key: "medicine", label: "💊 藥品" },
  { key: "document", label: "📄 文件" },
  { key: "other", label: "📌 其他" },
];

const CATEGORY_LABELS: Record<string, string> = {
  clothing: "👕 衣物",
  toiletries: "🧴 盥洗",
  electronics: "📱 3C",
  medicine: "💊 藥品",
  document: "📄 文件",
  other: "📌 其他",
};

const CATEGORY_COLORS: Record<string, string> = {
  clothing: "bg-blue-100",
  toiletries: "bg-green-100",
  electronics: "bg-purple-100",
  medicine: "bg-red-100",
  document: "bg-yellow-100",
  other: "bg-gray-100",
};

const filteredItems = computed(() => {
  if (activeFilter.value === "all") return items.value;
  return items.value.filter((i) => i.category === activeFilter.value);
});

const groupedItems = computed(() => {
  const groups: Record<string, PackingItem[]> = {};
  const cats = activeFilter.value === "all" ? PACKING_CATEGORIES : [activeFilter.value];
  for (const cat of cats) {
    const catItems = filteredItems.value.filter((i) => i.category === cat);
    if (catItems.length > 0) groups[cat] = catItems;
  }
  return groups;
});

const totalItems = computed(() => items.value.length);
const checkedItems = computed(() => items.value.filter((i) => i.checked).length);
const progressPercent = computed(() =>
  totalItems.value > 0 ? Math.round((checkedItems.value / totalItems.value) * 100) : 0,
);
const allChecked = computed(() => totalItems.value > 0 && checkedItems.value === totalItems.value);

async function fetchItems() {
  loading.value = true;
  try {
    const res = await packingApi.list(props.tripId);
    items.value = res.data;
  } catch {
    items.value = [];
    addToast("error", "載入打包清單失敗");
  } finally {
    loading.value = false;
  }
}

async function toggleItem(item: PackingItem) {
  const oldChecked = item.checked;
  item.checked = !item.checked;
  try {
    await packingApi.update(item.id, { checked: item.checked });
  } catch {
    item.checked = oldChecked;
    addToast("error", "更新失敗");
  }
}

async function handleAdd() {
  if (!newName.value.trim()) return;
  try {
    await packingApi.create(props.tripId, {
      name: newName.value.trim(),
      category: newCategory.value,
      quantity: newQuantity.value,
    });
    showAddModal.value = false;
    newName.value = "";
    newCategory.value = "clothing";
    newQuantity.value = 1;
    await fetchItems();
    addToast("success", "已新增打包項目");
  } catch {
    addToast("error", "新增失敗");
  }
}

async function handleDelete(itemId: string) {
  try {
    await packingApi.delete(itemId);
    await fetchItems();
    addToast("success", "已刪除項目");
  } catch {
    addToast("error", "刪除失敗");
  }
}

async function handleBatchToggle(checked: boolean) {
  const itemIds = items.value.map((i) => i.id);
  if (itemIds.length === 0) return;
  try {
    await packingApi.batchToggle(props.tripId, itemIds, checked);
    items.value.forEach((i) => (i.checked = checked));
    addToast("success", checked ? "已全部打勾" : "已全部取消");
  } catch {
    addToast("error", "批次操作失敗");
  }
}

onMounted(fetchItems);
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-900">📦 打包清單</h2>
      <button
        @click="showAddModal = true"
        class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
      >
        ＋ 新增
      </button>
    </div>

    <!-- Progress -->
    <div class="mb-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div class="mb-2 flex items-center justify-between text-sm">
        <span class="text-gray-600">已打包 {{ checkedItems }}/{{ totalItems }} 項</span>
        <span class="font-semibold text-gray-900">{{ progressPercent }}%</span>
      </div>
      <div class="h-2.5 overflow-hidden rounded-full bg-gray-100">
        <div
          class="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
    </div>

    <!-- Batch Toggle + Filter Tabs -->
    <div class="mb-4 flex items-center justify-between gap-2">
      <button
        v-if="totalItems > 0"
        @click="handleBatchToggle(!allChecked)"
        class="whitespace-nowrap rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50"
      >
        {{ allChecked ? "全部取消" : "全部打勾" }}
      </button>
      <div v-else></div>
      <div class="flex gap-1 overflow-x-auto">
        <button
          v-for="f in CATEGORY_FILTERS"
          :key="f.key"
          @click="activeFilter = f.key"
          :class="[
            'whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition',
            activeFilter === f.key
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
          ]"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i">
        <SkeletonLoader :lines="2" />
      </div>
    </div>

    <!-- Empty -->
    <EmptyState
      v-else-if="items.length === 0"
      icon="🎒"
      title="尚未新增打包項目"
      description="按「＋ 新增」開始整理行李"
      actionText="新增項目"
      @action="showAddModal = true"
    />
    <EmptyState
      v-else-if="filteredItems.length === 0"
      icon="🔍"
      title="此分類尚無項目"
      description="試試看其他分類"
    />

    <!-- Groups -->
    <div v-else class="space-y-4">
      <div v-for="(catItems, cat) in groupedItems" :key="cat">
        <h3
          :class="[
            'mb-2 inline-block rounded-lg px-3 py-1 text-xs font-semibold',
            CATEGORY_COLORS[cat] || CATEGORY_COLORS.other,
          ]"
        >
          {{ CATEGORY_LABELS[cat] || cat }}
        </h3>
        <div class="space-y-1.5">
          <div
            v-for="item in catItems"
            :key="item.id"
            class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm transition hover:border-indigo-200"
          >
            <input
              type="checkbox"
              :checked="item.checked"
              @change="toggleItem(item)"
              class="h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span
              class="flex-1 text-sm"
              :class="item.checked ? 'text-gray-400 line-through' : 'text-gray-900'"
            >
              {{ item.name }}
              <span v-if="item.quantity > 1" class="ml-1 text-xs text-gray-400"
                >×{{ item.quantity }}</span
              >
            </span>
            <button
              @click="handleDelete(item.id)"
              class="text-gray-300 hover:text-red-500"
              title="刪除"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="showAddModal = false"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-bold">新增打包項目</h3>
        <form @submit.prevent="handleAdd" class="space-y-3">
          <input
            v-model="newName"
            placeholder="項目名稱"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
          />

          <div class="flex gap-2">
            <div class="flex-1">
              <label class="mb-1 block text-xs text-gray-500">類別</label>
              <select
                v-model="newCategory"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              >
                <option
                  v-for="cat in PACKING_CATEGORIES"
                  :key="cat"
                  :value="cat"
                >
                  {{ CATEGORY_LABELS[cat] }}
                </option>
              </select>
            </div>
            <div class="w-24">
              <label class="mb-1 block text-xs text-gray-500">數量</label>
              <input
                v-model.number="newQuantity"
                type="number"
                min="1"
                max="99"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>
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
  </div>
</template>
