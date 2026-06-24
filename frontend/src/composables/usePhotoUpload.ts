import { ref } from "vue";
import api from "../api/client";

export function usePhotoUpload(maxPhotos = 9) {
  const uploading = ref(false);
  const photos = ref<string[]>([]); // blob URLs for preview

  async function handleFileSelect(e: Event) {
    const files = (e.target as HTMLInputElement).files;
    if (!files) return;
    for (const file of Array.from(files)) {
      if (photos.value.length >= maxPhotos) break;
      const url = URL.createObjectURL(file);
      photos.value.push(url);
    }
  }

  function removePhoto(index: number) {
    URL.revokeObjectURL(photos.value[index]);
    photos.value.splice(index, 1);
  }

  async function uploadPhotos(): Promise<string[]> {
    uploading.value = true;
    const urls: string[] = [];
    try {
      for (const blobUrl of photos.value) {
        const resp = await fetch(blobUrl);
        const blob = await resp.blob();
        const formData = new FormData();
        formData.append("file", blob, `photo-${Date.now()}.jpg`);
        const result = await api.post("/files/upload", formData);
        urls.push(result.data.url);
      }
    } finally {
      uploading.value = false;
    }
    return urls;
  }

  function reset() {
    photos.value.forEach((url) => URL.revokeObjectURL(url));
    photos.value = [];
  }

  return { uploading, photos, handleFileSelect, removePhoto, uploadPhotos, reset };
}
