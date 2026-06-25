import { ref, computed } from "vue";
import { memoryApi } from "../api/client";
import { usePhotoUpload } from "./usePhotoUpload";
import { useToast } from "./useToast";
import { trimmed, trimmedOrUndefined } from "../utils/trim";
import type { Memory } from "../types";

export function useTripMemories(tripId: string) {
  const { add: addToast } = useToast();
  const memories = ref<Memory[]>([]);
  const memoriesLoading = ref(false);
  const showAddMemory = ref(false);
  const newMemTitle = ref("");
  const newMemContent = ref("");
  const newMemDate = ref("");
  const { photos: newMemPhotos, handleFileSelect, removePhoto, uploadPhotos, reset: resetPhotos } = usePhotoUpload();

  const allTripPhotos = computed(() => {
    const photos: Array<{ url: string; user_name: string; date: string }> = [];
    for (const m of memories.value) {
      if (m.photo_urls && m.photo_urls.length > 0) {
        for (const url of m.photo_urls) {
          photos.push({ url, user_name: m.user_name, date: m.date });
        }
      }
    }
    return photos;
  });

  async function fetchMemories() {
    memoriesLoading.value = true;
    try {
      const res = await memoryApi.list(tripId);
      memories.value = res.data;
    } catch {
      memories.value = [];
    } finally {
      memoriesLoading.value = false;
    }
  }

  async function handleAddMemory() {
    if (!newMemTitle.value || !newMemDate.value) return;
    try {
      let photoUrls: string[] | undefined;
      if (newMemPhotos.value.length > 0) {
        photoUrls = await uploadPhotos();
      }
      await memoryApi.create(tripId, {
        title: trimmed(newMemTitle.value),
        content: trimmedOrUndefined(newMemContent.value),
        date: newMemDate.value,
        photo_urls: photoUrls,
      });
      showAddMemory.value = false;
      newMemTitle.value = "";
      newMemContent.value = "";
      newMemDate.value = "";
      resetPhotos();
      await fetchMemories();
    } catch {
      addToast("error", "新增回憶失敗");
    }
  }

  async function handleDeleteMemory(memoryId: string) {
    try {
      await memoryApi.delete(memoryId);
      await fetchMemories();
    } catch {
      addToast("error", "刪除回憶失敗");
    }
  }

  return {
    memories, memoriesLoading,
    showAddMemory, newMemTitle, newMemContent, newMemDate,
    newMemPhotos, handleFileSelect, removePhoto,
    allTripPhotos,
    fetchMemories, handleAddMemory, handleDeleteMemory,
  };
}