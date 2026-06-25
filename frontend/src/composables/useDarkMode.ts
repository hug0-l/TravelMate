import { ref, watchEffect } from "vue";

const isDark = ref(localStorage.getItem("dark-mode") === "true");

watchEffect(() => {
  document.documentElement.classList.toggle("dark", isDark.value);
  localStorage.setItem("dark-mode", String(isDark.value));
});

export function useDarkMode() {
  function toggle() {
    isDark.value = !isDark.value;
  }

  return { isDark, toggle };
}