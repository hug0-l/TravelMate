import { ref } from "vue";

export interface Toast {
  id: number;
  type: "success" | "error" | "info" | "warning";
  message: string;
}

const toasts = ref<Toast[]>([]);
let nextId = 0;

export function useToast() {
  function add(type: Toast["type"], message: string) {
    const id = nextId++;
    toasts.value.push({ id, type, message });
    setTimeout(() => remove(id), 3500);
  }

  function remove(id: number) {
    const idx = toasts.value.findIndex((t) => t.id === id);
    if (idx !== -1) toasts.value.splice(idx, 1);
  }

  return { toasts, add, remove };
}
